import chromadb # type: ignore
import os

def get_db():
    # We use the absolute path inside the Docker container
    # This ensures there are no folder-not-found errors
    db_path = "/app/.chroma_db"

    # Initialize the persistent client
    client = chromadb.PersistentClient(path=db_path)
    # Create or retrieve the collection
    collection = client.get_or_create_collection(name="note_ricerca")
    return collection

def sync_notes():
    """
    Syncs the database (ChromaDB) with the physical folders:
    1. Removes notes deleted on disk.
    2. Adds new notes created on disk.
    3. Updates notes modified on disk.
    """
    import uuid
    import time

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
            # If it's an update, first delete the old ids from the DB
            if is_updated:
                collection.delete(ids=db_files[file]["ids"])
                updated_count += 1
            else:
                added_count += 1

            # Read the content and insert it into the DB
            try:
                with open(data["path"], 'r', encoding="utf-8") as f:
                    content = f.read()

                # Note: This is a raw "document level" insertion.
                # If the files are very long you should chunk them first.
                collection.add(
                    documents=[content],
                    metadatas=[{"source": file, "mtime": data["mtime"]}],
                    ids=[str(uuid.uuid4())]
                )
            except Exception as e:
                print(f"❌ Error while syncing {file}: {e}")

    # Output the result
    if added_count == 0 and updated_count == 0 and not ids_to_delete:
        print("✅ No new notes to sync. The database is up to date.")
    else:
        print(f"✅ Sync complete! New: {added_count}, Updated: {updated_count}, Deleted: {len(deleted_files)}")

if __name__ == "__main__":
    coll = get_db()
    print(f"✅ Connection established. Notes present: {coll.count()}")