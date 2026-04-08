import chromadb # type: ignore
import os

def get_db():
    # Usiamo il percorso assoluto interno al container Docker
    # Questo garantisce che non ci siano errori di cartelle non trovate
    db_path = "/app/.chroma_db"
    
    # Inizializza il client persistente
    client = chromadb.PersistentClient(path=db_path)
    # Crea o recupera la collezione
    collection = client.get_or_create_collection(name="note_ricerca")
    return collection

def sync_notes():
    """
    Sincronizza il database (ChromaDB) con le cartelle fisiche:
    1. Rimuove le note eliminate su disco.
    2. Aggiunge le nuove note create su disco.
    3. Aggiorna le note modificate su disco.
    """
    import uuid
    import time
    
    collection = get_db()
    
    # 1. Ottieni i dati attualmente nel DB
    db_data = collection.get()
    db_metadatas = db_data.get("metadatas", [])
    db_ids = db_data.get("ids", [])
    
    # Mappiamo i source_file presenti nel DB con i loro ID e mtime
    # source_file -> {"ids": [...], "mtime": ...}
    db_files = {}
    for i, meta in enumerate(db_metadatas):
        if meta and "source" in meta:
            source = os.path.basename(meta["source"])
            if source not in db_files:
                db_files[source] = {"ids": [], "mtime": meta.get("mtime", 0)}
            db_files[source]["ids"].append(db_ids[i])
            
            # Se la nota ha più chunk, teniamo il mtime più recente trovato
            current_mtime = meta.get("mtime", 0)
            if current_mtime > db_files[source]["mtime"]:
                db_files[source]["mtime"] = current_mtime

    # 2. Scansiona le cartelle fisiche
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

    # 3. Elimina le note che non esistono più su disco
    ids_to_delete = []
    deleted_files = set()
    for source, data in db_files.items():
        if source not in existing_files:
            ids_to_delete.extend(data["ids"])
            deleted_files.add(source)
            
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        print(f"🗑️ Sync: Rimossi {len(deleted_files)} file non più presenti su disco.")

    # 4. Aggiungi le note nuove e aggiorna quelle modificate
    added_count = 0
    updated_count = 0
    
    for file, data in existing_files.items():
        is_new = file not in db_files
        # Aggiorniamo se il file su disco è più recente rispetto all'ultima sincronizzazione nel DB.
        # Spesso c'è una piccola discrepanza di float, usiamo una tolleranza di 1 secondo.
        is_updated = not is_new and data["mtime"] > db_files[file]["mtime"] + 1.0
        
        if is_new or is_updated:
            # Se è un aggiornamento, prima eliminiamo i vecchi id dal DB
            if is_updated:
                collection.delete(ids=db_files[file]["ids"])
                updated_count += 1
            else:
                added_count += 1
                
            # Leggiamo il contenuto e lo inseriamo nel DB
            try:
                with open(data["path"], 'r', encoding="utf-8") as f:
                    content = f.read()
                
                # Attenzione: Questo è un inserimento grezzo "document level". 
                # Se i file sono molto lunghi dovresti chunkarli prima.
                collection.add(
                    documents=[content],
                    metadatas=[{"source": file, "mtime": data["mtime"]}],
                    ids=[str(uuid.uuid4())]
                )
            except Exception as e:
                print(f"❌ Errore durante la sincronizzazione di {file}: {e}")

    # Output del risultato
    if added_count == 0 and updated_count == 0 and not ids_to_delete:
        print("✅ Nessuna nuova nota da sincronizzare. Il database è aggiornato.")
    else:
        print(f"✅ Sync completo! Nuove: {added_count}, Aggiornate: {updated_count}, Eliminate: {len(deleted_files)}")

if __name__ == "__main__":
    coll = get_db()
    print(f"✅ Connessione stabilita. Note presenti: {coll.count()}")