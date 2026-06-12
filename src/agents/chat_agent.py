import os
from src.database.vector_db import get_db
from src.config.llm_manager import get_llm_model
from agno.agent import Agent # type: ignore
from agno.tools.duckduckgo import DuckDuckGoTools # type: ignore
from src.tools.web_scraper import read_webpage # type: ignore

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")

def chat_with_brain(user_query):
    print(f"\n🔍 Searching the Second Brain for: '{user_query}'...")
    
    # 1. Connect to the local Database
    collection = get_db()

    # 2. Run the vector search (RAG - Retrieval)
    try:
        risultati = collection.query(query_texts=[user_query], n_results=3)
        if not risultati.get('documents') or len(risultati['documents'][0]) == 0:
            print("⚠️ No notes found in your database for this search.")
            return {
                "answer": "I couldn't find this information in your local notes. Do you want me to search the web?",
                "sources": [],
                "action_required": "web_search_button"
            }
    except Exception as e:
        print(f"⚠️ RAG error: {str(e)}") # This way if there's an error, you see what it is!
        return {"answer": "Error while searching the database.", "sources": []}

    # 3. Build the Context
    docs = risultati['documents'][0]
    metadatas = risultati['metadatas'][0]
    contesto_recuperato = ""
    fonti_dettagliate = [] # New list for the sources with their content

    for d, meta in zip(docs, metadatas):
        nome_fonte = meta['source']
        contesto_recuperato += f"\n\n--- FONTE: {nome_fonte} ---\n{d}"
        # Save both the name and the text snippet
        fonti_dettagliate.append({
            "source": nome_fonte,
            "content": d
        })

    print("🧠 Analyzing your notes (Agno Agent)...")

    # 4. Create the Agno Agent for the chat
    chat_agent = Agent(
        name="Second Brain Assistant",
        role="Studente Universitario Assistente",
        model=get_llm_model(),
        instructions=[
            "Sei un assistente brillante collegato al Second Brain dell'utente.",
            "Rispondi alle domande basandoti ESCLUSIVAMENTE sul contesto fornito.",
            "Se la risposta NON è nel contesto, rispondi ESATTAMENTE con la stringa 'REQUIRE_WEB_SEARCH'. Non aggiungere altro.",
            "Non inventare risposte e non usare conoscenze esterne."
        ]
    )
    
    # 5. Generate the response
    prompt = f"CONTESTO DAL VAULT:\n{contesto_recuperato}\n\nDOMANDA DELL'UTENTE:\n{user_query}"
    response = chat_agent.run(prompt)

    # 6. Return or print the response
    answer = response.content.strip()

    if "REQUIRE_WEB_SEARCH" in answer:
        return {
            "answer": "I couldn't find this information in your local notes. Do you want me to search the web?",
            "sources": [],
            "action_required": "web_search_button"
        }
    
    return {"answer": answer, "sources": fonti_dettagliate}

def chat_with_web(user_query):
    print(f"\n🌐 Web Search initiated for: '{user_query}'...")
    
    web_agent = Agent(
        name="Web Researcher Assistant",
        role="Ricercatore Web",
        model=get_llm_model(),
        tools=[DuckDuckGoTools(), read_webpage],
        instructions=[
            "Sei un assistente alla ricerca web. Rispondi alla domanda dell'utente cercando informazioni aggiornate su internet.",
            "Usa il tool DuckDuckGo per cercare e il tool read_webpage per leggere i contenuti dei siti.",
            "Fornisci una risposta chiara, riassuntiva e cita le fonti (gli URL che hai consultato)."
        ]
    )
    
    response = web_agent.run(user_query)
    answer = response.content.strip()
    
    return {"answer": answer, "sources": [], "action_required": None}