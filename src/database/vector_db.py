import chromadb # type: ignore
import os
import re
import uuid

# Absolute path inside the Docker container (avoids folder-not-found errors)
DB_PATH = "/app/.chroma_db"
COLLECTION_NAME = "note_ricerca"


def get_embedding_function():
    """Local, multilingual embedding function served through Ollama.

    Defaults to `nomic-embed-text` (768-dim, multilingual) so retrieval works
    well on non-English notes while staying 100% local. Configurable via
    `EMBED_MODEL` in `.env`. Returns None if the function can't be built so the
    caller can fall back to ChromaDB's bundled default model.
    """
    model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    try:
        from chromadb.utils.embedding_functions import OllamaEmbeddingFunction  # type: ignore
        # `url` is the Ollama base URL; the function appends the embeddings endpoint.
        return OllamaEmbeddingFunction(url=ollama_host, model_name=model)
    except Exception as e:
        print(f"⚠️ Ollama embedding function unavailable ({e}). Falling back to ChromaDB default model.")
        return None


def get_db():
    # Initialize the persistent client
    client = chromadb.PersistentClient(path=DB_PATH)
    # Create or retrieve the collection, embedding via the local Ollama model
    ef = get_embedding_function()
    if ef is None:
        return client.get_or_create_collection(name=COLLECTION_NAME)

    try:
        return client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)
    except ValueError as e:
        # An older DB was indexed with a different embedding model (e.g. ChromaDB's
        # default 384-dim MiniLM). The embedding function / vector dimensionality
        # no longer matches, so we reset the collection and let the next sync
        # re-index every note from disk with the new model.
        if "embedding function" not in str(e).lower():
            raise
        print("♻️ Embedding model changed — resetting the vector collection. "
              "Run a sync to re-index your notes (sources on disk are untouched).")
        client.delete_collection(name=COLLECTION_NAME)
        return client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)


def chunk_text(text, chunk_size=None, overlap=None):
    """Split text into overlapping chunks for sharper retrieval.

    Splits on heading/paragraph boundaries first, then packs blocks up to
    ~`chunk_size` words with ~`overlap` words of carry-over between chunks.
    Oversized single blocks are hard-split. Sizes are in words (~0.75 tokens
    each) and configurable via `CHUNK_SIZE` / `CHUNK_OVERLAP` in `.env`.
    """
    if chunk_size is None:
        chunk_size = int(os.getenv("CHUNK_SIZE", "600"))
    if overlap is None:
        overlap = int(os.getenv("CHUNK_OVERLAP", "80"))
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 10)

    text = (text or "").strip()
    if not text:
        return []

    # Split on blank lines so headings/paragraphs stay intact
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

    chunks = []
    current = []          # list of block strings in the current chunk
    current_len = 0       # word count of current chunk

    def flush():
        nonlocal current, current_len
        if current:
            chunks.append("\n\n".join(current))
        current, current_len = [], 0

    for block in blocks:
        words = block.split()
        wlen = len(words)

        # A single block larger than chunk_size: flush, then hard-split it
        if wlen > chunk_size:
            flush()
            step = chunk_size - overlap if chunk_size > overlap else chunk_size
            for i in range(0, wlen, step):
                chunks.append(" ".join(words[i:i + chunk_size]))
            continue

        # Adding this block would overflow the current chunk -> flush with overlap
        if current_len + wlen > chunk_size and current:
            chunks.append("\n\n".join(current))
            tail_words = "\n\n".join(current).split()[-overlap:] if overlap > 0 else []
            current = [" ".join(tail_words)] if tail_words else []
            current_len = len(tail_words)

        current.append(block)
        current_len += wlen

    flush()
    return [c for c in chunks if c.strip()]


def add_document(collection, content, source, extra_metadata=None, mtime=None):
    """Chunk `content` and add every chunk to the collection.

    Each chunk stores `source`, `chunk_index` and `chunk_total` so retrieved
    passages still resolve back to the origin note. Returns the list of chunk ids.
    """
    chunks = chunk_text(content)
    if not chunks:
        return []

    documents, metadatas, ids = [], [], []
    total = len(chunks)
    for idx, chunk in enumerate(chunks):
        meta = {"source": source, "chunk_index": idx, "chunk_total": total}
        if mtime is not None:
            meta["mtime"] = mtime
        if extra_metadata:
            meta.update(extra_metadata)
        documents.append(chunk)
        metadatas.append(meta)
        ids.append(str(uuid.uuid4()))

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return ids


def sync_notes():
    """
    Syncs the database (ChromaDB) with the physical folders:
    1. Removes notes deleted on disk.
    2. Adds new notes created on disk.
    3. Updates notes modified on disk.

    Notes are chunked before embedding, so each file maps to one or more
    chunk-ids in the DB. The delete/update logic groups ids by source file.
    """
    collection = get_db()

    # 1. Get the data currently in the DB
    db_data = collection.get()
    db_metadatas = db_data.get("metadatas", [])
    db_ids = db_data.get("ids", [])

    # Map the source_files present in the DB with their IDs and mtime
    # source_file -> {"ids": [...], "mtime": ...}
    db_files = {}
    for i, meta in enumerate(db_metadatas):
        if meta and "source" in meta:
            source = os.path.basename(meta["source"])
            if source not in db_files:
                db_files[source] = {"ids": [], "mtime": meta.get("mtime", 0)}
            db_files[source]["ids"].append(db_ids[i])

            # If the note has multiple chunks, keep the most recent mtime found
            current_mtime = meta.get("mtime", 0)
            if current_mtime > db_files[source]["mtime"]:
                db_files[source]["mtime"] = current_mtime

    # 2. Scan the physical folders
    existing_files = {}
    target_dirs = ["/app/notes", "/app/inbox"]

    for t_dir in target_dirs:
        if not os.path.exists(t_dir):
            continue
        for root, dirs, files in os.walk(t_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    mtime = os.path.getmtime(full_path)
                    existing_files[file] = {
                        "path": full_path,
                        "mtime": mtime
                    }

    # 3. Delete the notes that no longer exist on disk
    ids_to_delete = []
    deleted_files = set()
    for source, data in db_files.items():
        if source not in existing_files:
            ids_to_delete.extend(data["ids"])
            deleted_files.add(source)

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        print(f"🗑️ Sync: Removed {len(deleted_files)} files no longer present on disk.")

    # 4. Add the new notes and update the modified ones
    added_count = 0
    updated_count = 0

    for file, data in existing_files.items():
        is_new = file not in db_files
        # We update if the file on disk is more recent than the last sync in the DB.
        # There is often a small float discrepancy, so we use a tolerance of 1 second.
        is_updated = not is_new and data["mtime"] > db_files[file]["mtime"] + 1.0

        if is_new or is_updated:
            # If it's an update, first delete the old (possibly multiple) chunk-ids
            if is_updated:
                collection.delete(ids=db_files[file]["ids"])
                updated_count += 1
            else:
                added_count += 1

            # Read the content, chunk it, and insert it into the DB
            try:
                with open(data["path"], 'r', encoding="utf-8") as f:
                    content = f.read()

                add_document(collection, content, file, mtime=data["mtime"])
            except Exception as e:
                print(f"❌ Error while syncing {file}: {e}")

    # Output the result
    if added_count == 0 and updated_count == 0 and not ids_to_delete:
        print("✅ No new notes to sync. The database is up to date.")
    else:
        print(f"✅ Sync complete! New: {added_count}, Updated: {updated_count}, Deleted: {len(deleted_files)}")

    return {
        "added": added_count,
        "updated": updated_count,
        "deleted": len(deleted_files),
        "total": collection.count(),
    }


if __name__ == "__main__":
    coll = get_db()
    print(f"✅ Connection established. Notes present: {coll.count()}")
