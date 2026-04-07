import chromadb # type: ignore
import os

def get_db():
    # Inizializza il client persistente (salva i dati su disco)
    client = chromadb.PersistentClient(path="./.chroma_db")
    # Crea o recupera la collezione "note_ricerca"
    collection = client.get_or_create_collection(name="note_ricerca")
    return collection

def sync_deleted_notes():
    """
    Rimuove dal database (ChromaDB) tutte le note che sono state
    cancellate fisicamente dalla cartella 'notes' o 'inbox'.
    """
    collection = get_db()
    
    # 1. Ottieni tutti gli elementi attualmente nel database
    db_data = collection.get()
    db_metadatas = db_data.get("metadatas", [])
    db_ids = db_data.get("ids", [])
    
    if not db_metadatas:
        print("Il database è vuoto. Nessuna sincronizzazione necessaria.")
        return

    # 2. Ottieni la lista di tutti i file markdown nell'intero progetto (Vault)
    existing_files = set()
    
    # Scansiona partendo dalla directory corrente (la radice del progetto)
    for root, dirs, files in os.walk("."):
        # Evita di scansionare cartelle di sistema, nascoste o virtual environment
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ["venv", "__pycache__"]]
        
        for file in files:
            if file.endswith(".md"):
                # Salviamo solo il nome del file (es: new_note_0.md)
                existing_files.add(file)
        
    # 3. Trova gli ID delle note nel DB che non esistono più fisicamente
    ids_to_delete = []
    deleted_files = set()
    
    for i, meta in enumerate(db_metadatas):
        if meta and "source" in meta:
            source_file = meta["source"]  # Questo è solitamente solo il nome del file
            
            # Per sicurezza estraiamo solo il nome base nel caso in cui source avesse un percorso intero
            base_name = os.path.basename(source_file)
            
            if base_name not in existing_files:
                ids_to_delete.append(db_ids[i])
                deleted_files.add(source_file)
                
    # 4. Rimuovili dal database
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        print(f"🗑️ Rimossi dal database {len(ids_to_delete)} elementi obsoleti.")
        print(f"File non più presenti eliminati: {', '.join(deleted_files)}")
    else:
        print("✅ Database e file system sono già perfettamente sincronizzati.")

if __name__ == "__main__":
    coll = get_db()
    print("✅ Database Vettoriale Inizializzato con successo!")
    # Puoi chiamare questo per pulire tutto manualmente
    sync_deleted_notes()