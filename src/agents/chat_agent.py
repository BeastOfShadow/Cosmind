import os
from src.database.vector_db import get_db
from src.config.llm_manager import get_llm_model
from agno.agent import Agent # type: ignore

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")

def chat_with_brain(user_query):
    print(f"\n🔍 Searching the Second Brain for: '{user_query}'...")
    
    # 1. Connettiti al Database locale
    collection = get_db()
    
    # 2. Fai la ricerca vettoriale (RAG - Retrieval)
    try:
        risultati = collection.query(query_texts=[user_query], n_results=3)
        if not risultati.get('documents') or len(risultati['documents'][0]) == 0:
            print("⚠️ Nessuna nota trovata nel tuo database per questa ricerca.")
            return {"answer": "Non ho trovato informazioni rilevanti nei tuoi appunti.", "sources": []}
    except Exception as e:
        print(f"⚠️ Errore RAG: {str(e)}") # Così se c'è un errore, vedi quale è!
        return {"answer": "Errore durante la ricerca nel database.", "sources": []}
        
    # 3. Costruisci il Contesto
    docs = risultati['documents'][0]
    fonti = [meta['source'] for meta in risultati['metadatas'][0]]
    
    contesto_recuperato = ""
    for d, f in zip(docs, fonti):
        contesto_recuperato += f"\n\n--- FONTE: {f} ---\n{d}"
    
    print("🧠 Sto analizzando le tue note (Agno Agent)...")
    
    # 4. Crea l'Agente Agno per la chat
    chat_agent = Agent(
        name="Second Brain Assistant",
        role="Studente Universitario Assistente",
        model=get_llm_model(),
        instructions=[
            "Sei un assistente brillante collegato al Second Brain dell'utente.",
            "Rispondi alle domande basandoti ESCLUSIVAMENTE sul contesto fornito.",
            "Se la risposta non è nel contesto, rispondi 'Non ho questa informazione nei tuoi appunti'.",
            "Non inventare risposte e non usare conoscenze esterne."
        ]
    )
    
    # 5. Genera la risposta
    prompt = f"CONTESTO DAL VAULT:\n{contesto_recuperato}\n\nDOMANDA DELL'UTENTE:\n{user_query}"
    response = chat_agent.run(prompt)
    
    # 6. Restituisci o stampa la risposta
    answer = response.content.strip()
    sources = list(set(fonti))
    
    print("\n================ ANSWER ================\n")
    print(answer)
    print("\n========================================\n")
    print(f"📚 Sources used: {', '.join(sources)}")
    
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    print("🤖 Welcome to your Agno Second Brain Chat!")
    while True:
        try:
            domanda = input("\nAsk a question (or type 'exit' to quit): ")
            if domanda.lower() == 'exit':
                break
            if domanda.strip():
                chat_with_brain(domanda)
        except KeyboardInterrupt:
            break