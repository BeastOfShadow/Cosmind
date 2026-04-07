import os
from database_manager import get_db
from llm_manager import ask_llm

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")

def chat_with_brain(user_query):
    print(f"\n🔍 Searching the Second Brain for: '{user_query}'...")
    
    # 1. Connettiti al Database
    collection = get_db()
    
    # 2. Fai la ricerca vettoriale (RAG - Retrieval)
    # ChromaDB trasforma la tua domanda in numeri e trova i 3 documenti più simili
    risultati = collection.query(
        query_texts=[user_query],
        n_results=3 # Numero di note da recuperare
    )
    
    # Se il database è vuoto o non trova nulla
    if not risultati['documents'][0]:
        print("⚠️ No relevant notes found in your database.")
        return
        
    # 3. Unisci le note trovate in un unico "Contesto"
    contesto_recuperato = "\n\n--- NEXT NOTE ---\n\n".join(risultati['documents'][0])
    
    print("🧠 Thinking and analyzing your notes...")
    
    # 4. Costruisci il Prompt per l'LLM (Augmented Generation)
    prompt = f"""You are a brilliant AI assistant connected to a student's Second Brain (personal notes).
    Answer the user's question using ONLY the information provided in the context below.
    If the answer is not contained in the context, say "I don't have this information in your notes."
    Do not use outside knowledge.
    
    CONTEXT (Your notes):
    {contesto_recuperato}
    
    USER QUESTION:
    {user_query}
    """
    
    # 5. Genera la risposta
    content = ask_llm(prompt)
    
    # 6. Stampa il risultato
    print("\n================ ANSWER ================\n")
    print(content)
    print("\n========================================\n")
    
    # (Opzionale) Stampa le fonti usate
    fonti = [meta['source'] for meta in risultati['metadatas'][0]]
    print(f"📚 Sources used: {', '.join(set(fonti))}")

if __name__ == "__main__":
    print("🤖 Welcome to your Second Brain Chat!")
    while True:
        domanda = input("\nAsk a question (or type 'exit' to quit): ")
        if domanda.lower() == 'exit':
            break
        chat_with_brain(domanda)