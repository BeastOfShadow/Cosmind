import chromadb # type: ignore

def check_my_brain():
    # 1. Connection
    client = chromadb.PersistentClient(path="./.chroma_db")

    # 2. See which collections exist
    collections = client.list_collections()
    print(f"📁 Collections found: {[c.name for c in collections]}")

    if not collections:
        print("❌ The database is completely empty (no collection).")
        return

    # 3. Check the specific collection
    coll = client.get_collection(name="note_ricerca")
    count = coll.count()
    print(f"📊 Number of indexed notes: {count}")

    if count > 0:
        print("\n📝 Preview of the first 3 notes:")
        data = coll.peek(3) # Gets the first 3
        for i in range(len(data['documents'])):
            print(f"--- Note {i+1} ---")
            print(f"File: {data['metadatas'][i]['source']}")
            print(f"Text: {data['documents'][i][:100]}...")
    else:
        print("⚠️ The collection exists but contains 0 items.")

if __name__ == "__main__":
    check_my_brain()