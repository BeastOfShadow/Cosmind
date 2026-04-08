import chromadb # type: ignore

def check_my_brain():
    # 1. Connessione
    client = chromadb.PersistentClient(path="./.chroma_db")
    
    # 2. Vediamo che collezioni esistono
    collections = client.list_collections()
    print(f"📁 Collezioni trovate: {[c.name for c in collections]}")
    
    if not collections:
        print("❌ Il database è totalmente vuoto (nessuna collezione).")
        return

    # 3. Controlliamo la collezione specifica
    coll = client.get_collection(name="note_ricerca")
    count = coll.count()
    print(f"📊 Numero di note indicizzate: {count}")

    if count > 0:
        print("\n📝 Anteprima delle prime 3 note:")
        data = coll.peek(3) # Prende le prime 3
        for i in range(len(data['documents'])):
            print(f"--- Nota {i+1} ---")
            print(f"File: {data['metadatas'][i]['source']}")
            print(f"Testo: {data['documents'][i][:100]}...")
    else:
        print("⚠️ La collezione esiste ma contiene 0 elementi.")

if __name__ == "__main__":
    check_my_brain()