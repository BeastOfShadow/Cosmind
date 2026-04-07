import os
import uuid
import json
from datetime import datetime
from database_manager import get_db, sync_deleted_notes
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from llm_manager import ask_llm

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")

# Assicuriamoci che la cartella inbox esista
os.makedirs("inbox", exist_ok=True)

import glob
import shutil
import re
from urllib.parse import unquote

# 0. Sincronizza prima il DB (cancella eventuali note sparite dalla folder "notes" e "inbox")
print("🧹 Syncing Database con file locali...")
sync_deleted_notes()

def process_image(filepath, db):
    """
    Agente per analizzare un'immagine standalone.
    Estrae il testo ed indicizza nel DB.
    """
    print(f"\n📸 [Vision Agent] Analisi immagine: {filepath}")
    vision_prompt = """
    Sei un assistente per 'Second Brain' per Zettelkasten.
    Analizza l'immagine fornita. Se c'è testo riassumilo. 
    Descrivi la scena. Ritorna una struttura Markdown con: # Titolo Immagine, Descrizione dettagliata, Concetti chiave e Testo estratto.
    """
    
    try:
        from llm_manager import ask_llm
        image_content = ask_llm(vision_prompt, image_paths=[filepath])
        
        base_name = os.path.basename(filepath)
        note_name = f"image_note_{base_name}.md"
        out_path = os.path.join("notes", note_name) # salviamo in notes
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"---\ntags:\n  - status/1-draft\n  - image\n---\n\n![[{base_name}]]\n\n{image_content}")
            
        db.add(
            documents=[image_content],
            metadatas=[{"source": note_name, "type": "image_analysis"}],
            ids=[f"{base_name}_analysis"]
        )
        print(f"✅ Immagine processata e convertita in: {note_name}")
        
    except Exception as e:
        print(f"❌ Errore processamento immagine {filepath}: {e}")

def extract_and_solve_embedded_images(content, db):
    """
    Trova i link alle immagini in formato Obsidian (es. ![[immagine.png]]).
    Richiede al LLM Vision di analizzarle e memorizza il risultato come metadato.
    """
    regex = r'!\[\[(.*?\.(?:png|jpg|jpeg|gif|webp))\]\]'
    matches = re.findall(regex, content, re.IGNORECASE)
    
    from llm_manager import ask_llm
    
    for match in matches:
        print(f"🔍 [Embedded Vision Agent] Trovata immagine incorporata: ![[{match}]]")
        decoded_match = unquote(match) # Rimuovi %20 se ci sono spazi
        # Trova il file (cerca in tutta la root)
        search_pattern = f"**/{decoded_match}"
        found_files = glob.glob(search_pattern, recursive=True)
        
        if found_files:
            image_path = found_files[0]
            print(f"✅ Immagine trovata: {image_path}")
            vision_prompt = "Sei un analista per Second Brain. L'utente ha inserito questa immagine in una nota. Riassumi questa immagine concisamente in 3 righe per contestualizzarla per la RAG."
            try:
                 image_context = ask_llm(vision_prompt, image_paths=[image_path])
                 print(f"👁️ Immagine '{match}' tradotta in: {image_context[:50]}...")
                 
                 # Aggiungiamo il contesto visivo nascosto alla nota RAG
                 content = content.replace(f"![[{match}]]", f"![[{match}]]\n\n> [Vision Analysis]: {image_context}")
                 
                 # Aggiungila al VectorDB come blocco indipendente
                 db.add(
                    documents=[image_context],
                    metadatas=[{"source": match, "type": "embedded_image"}],
                    ids=[f"embedded_{match}_analysis"]
                 )
            except Exception as e:
                 print(f"❌ Errore Analisi Immagine Embedded: {e}")
        else:
             print(f"❌ Errore: File immagine non trovato nel Vault: {match}")
            
    return content

# --- AGENT 0: THE RESEARCHER (Context Retrieval) ---
def retrieve_context(raw_text):
    print("🔍 Researcher Agent: Searching the Vector DB for existing similar notes...")
    collection = get_db()
    try:
        results = collection.query(query_texts=[raw_text], n_results=3)
        if results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
            sources = results['metadatas'][0]
            context = ""
            for doc, meta in zip(docs, sources):
                context += f"\n### EXISTING NOTE: {meta['source']}\n{doc}\n"
            print("   -> Found existing context to avoid duplicates.")
            return context
    except Exception as e:
        print(f"   -> DB is empty or still initializing.")
    return "No existing notes found in the database."

# --- AGENT 1: THE SPLITTER (JSON Mode) ---
def agent_splitter(raw_text, existing_context):
    print("🤖 Splitter Agent: Extracting structured data (JSON)...")
    
    prompt = f"""You are an advanced data extraction engine. Analyze the RAW TEXT and output a SINGLE JSON OBJECT.
    DO NOT copy the schema examples. Extract ACTUAL data from the user's text.
    
    EXISTING NOTES:
    {existing_context}
    
    RAW TEXT:
    {raw_text}
    
    Return a JSON object strictly matching this schema type:
    {{
        "new_notes": [
            {{
                "filename": "string (format: concept_name.md)",
                "title": "string (the title of the concept)",
                "aliases": ["string", "string"],
                "domain": "string (e.g. backend, ai, frontend)",
                "tldr": "string (2 lines summary)",
                "body": "string (detailed markdown content)",
                "derives_from": ["string"],
                "leads_to": ["string"],
                "similar_to": ["string"]
            }}
        ],
        "updates": [
            {{
                "filename": "string (must be the exact name of an existing note)",
                "content_to_add": "string (the exact new text to append)"
            }}
        ]
    }}
    """
    
    try:
        content = ask_llm(prompt, require_json=True)
        return json.loads(content)
    except Exception as e:
        print(f"❌ Error: The model failed to generate valid JSON. Dettagli: {e}")
        return {"new_notes": [], "updates": []}

# --- AGENT 2: THE LIBRARIAN (Indexing) ---
def agent_librarian(filename, content):
    print(f"📚 Librarian Agent: Indexing {filename} into the Vector DB...")
    collection = get_db()
    collection.add(
        documents=[content],
        metadatas=[{"source": filename}],
        ids=[str(uuid.uuid4())]
    )

# --- AGENT 3: THE DEEP RESEARCHER (Web Scraping) ---
def agent_deep_researcher(concept_title, domain):
    print(f"🌐 Deep Researcher Agent: Scraping deep context for '{concept_title}'...")
    query = f"{concept_title} {domain} research paper OR documentation".strip()
    if not query:
        return "", []
    
    scraped_text = ""
    urls = []
    
    try:
        results = DDGS().text(query, max_results=2)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for res in results:
            url = res.get('href', '')
            if not url: continue
            
            urls.append(url)
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = " ".join([p.get_text() for p in soup.find_all('p')])
                scraped_text += f"\n--- Source: {url} ---\n{text[:2000]}\n"
            except Exception as e:
                print(f"   -> ⚠️  Failed to scrape {url}: {e}")
                
        return scraped_text, urls
    except Exception as e:
        print(f"   -> ⚠️  Web search failed: {e}")
        return "", []

# --- AGENT 4: THE WRITER (Synthesis) ---
def agent_writer(concept_title, user_raw_body, scraped_context):
    print(f"✍️ Writer Agent: Expanding note '{concept_title}' with web context...")
    prompt = f"""You are a personal knowledge management assistant. Your task is to expand the user's notes while STRICTLY MAINTAINING the user's original writing style, tone, and perspective.

    Rules:
    1. The USER'S RAW NOTES are your primary source of truth. You must write in the user's exact voice and style.
    2. Use the WEB RESEARCH CONTEXT ONLY to add accurate technical depth, examples, or missing details.
    3. IGNORE ANY SPAM OR OFF-TOPIC CONTENT in the web research (e.g., ignore random articles, foreign language lessons, or generic forums that don't strictly match the core concept).
    4. Do not sound like an AI or an academic textbook unless the user's raw notes sound like that. Write as if the user researched a bit more and expanded their own note.
    5. Do not include markdown headers like '# Body', just return the raw text.
    
    CONCEPT: {concept_title}
    
    USER'S RAW NOTES:
    {user_raw_body}
    
    WEB RESEARCH CONTEXT (Filter out garbage!):
    {scraped_context}
    """
    
    try:
        content = ask_llm(prompt)
        return content.strip()
    except Exception as e:
        print(f"   -> ❌ Writer failed: {e}")
        return user_raw_body

# --- AGENT 5: THE LECTURER (Literature Note) ---
def agent_literature_note(raw_text, original_filename, generated_notes):
    print(f"📑 Lecturer Agent: Generating Literature Note for '{original_filename}'...")
    
    # Se non ci sono note generate, non fa nulla
    if not generated_notes:
        return
        
    prompt = f"""You are a personal knowledge management assistant.
    Summarize the following RAW NOTES into a single comprehensive "Literature Note" or "Map of Content".
    Write a concise summary of the topics discussed. Mention the key takeaways.
    Format your response in Markdown without wrapping in quotes or codeblocks.
    
    RAW NOTES:
    {raw_text}
    """
    
    try:
        content = ask_llm(prompt)
        summary = content.strip()
    except Exception as e:
        print(f"   -> ❌ Literature summary failed: {e}")
        summary = "No summary generated."
        
    oggi = datetime.now()
    data_str = oggi.strftime("%Y-%m-%d")
    id_univoco = oggi.strftime("%Y%m%d%H%M%S")
    
    # Prepara i link alle note atomiche
    links_markdown = "\n".join([f"- [[{note.get('filename', '').replace('.md', '')}]] - *{note.get('title', '')}*" for note in generated_notes])
    
    lit_filename = f"LIT_{os.path.basename(original_filename)}"
    
    markdown_content = (
        "---\n"
        f"id: {id_univoco}\n"
        "tags:\n"
        "  - type/literature-note\n"
        "  - status/1-draft\n"
        f"created: {data_str}\n"
        f"modified: {data_str}\n"
        "---\n\n"
        f"# 📚 source: {original_filename}\n\n"
        "## 📝 Summary\n"
        f"{summary}\n\n"
        "---\n\n"
        "## 🔗 Atomic Concepts Extracted\n"
        "Questi sono i concetti chiave estratti da questa fonte:\n\n"
        f"{links_markdown}\n"
    )
    
    file_path = os.path.join("inbox", lit_filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"   -> 🆕 Generated Literature Note: {lit_filename}")
    
    # Indicizziamo la Literature Note (meno stringente la ricerca, ma fa contesto)
    agent_librarian(lit_filename, markdown_content)

# --- PYTHON FORMATTER: CREA I FILE DAL JSON ---
def create_markdown_files(parsed_data):
    print("💾 Python Formatter: Generating Markdown files...")
    
    oggi = datetime.now()
    data_str = oggi.strftime("%Y-%m-%d")
    id_univoco = oggi.strftime("%Y%m%d%H%M%S") # Es: 20260407165012
    
   # 1. Processa le NOTE NUOVE
    for index, nota in enumerate(parsed_data.get('new_notes', [])):
        filename = nota.get('filename', f"new_note_{index}.md").strip()
        
        # Gestisci le liste formattandole per i wikilinks
        derives = ", ".join([f"[[{x}]]" for x in nota.get('derives_from', [])])
        leads = ", ".join([f"[[{x}]]" for x in nota.get('leads_to', [])])
        similar = ", ".join([f"[[{x}]]" for x in nota.get('similar_to', [])])
        aliases = ", ".join([f'"{x}"' for x in nota.get('aliases', [])])
        
        scraped_text, urls = agent_deep_researcher(nota.get('title', ''), nota.get('domain', ''))
        expanded_body = agent_writer(nota.get('title', ''), nota.get('body', ''), scraped_text)
        urls_markdown = "\n".join([f"- {url}" for url in urls])
        
        # Costruzione sicura della stringa (zero problemi di indentazione)
        markdown_content = (
            "---\n"
            f"id: {id_univoco}\n"
            f"aliases: [{aliases}]\n"
            "tags:\n"
            "  - status/1-draft\n"
            f"  - domain/{nota.get('domain', 'general')}\n"
            f"created: {data_str}\n"
            f"modified: {data_str}\n"
            "---\n\n"
            f"# 📌 {nota.get('title', 'Untitled Concept')}\n\n"
            "## 🧠 TL;DR\n"
            "> [!summary] Abstract\n"
            f"> {nota.get('tldr', '')}\n\n"
            "---\n\n"
            "## 📝 Body\n"
            f"{expanded_body}\n\n"
            "---\n\n"
            "## 🔗 Knowledge Graph\n"
            f"- **Derives from (Base):** {derives}\n"
            f"- **Leads to (Developments):** {leads}\n"
            f"- **Similar concepts:** {similar}\n\n"
            "## 📚 Sources & References\n"
            "- User's raw notes\n"
            f"{urls_markdown}\n"
        )
        
        # Salviamo il file
        file_path = os.path.join("inbox", filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"   -> 🆕 Generated new note: {filename}")
        
        # Passiamo al DB
        agent_librarian(filename, markdown_content)
        
    # 2. Processa gli AGGIORNAMENTI
    for update in parsed_data.get('updates', []):
        filename = update.get('filename', '').strip()
        content = update.get('content_to_add', '').strip()
        
        # Sanitization strict check
        if not filename or not content:
            print(f"   -> ⏭️ Skipped ghost update due to empty filename or content")
            continue
            
        if "string (" in filename or "unknown.md" in filename:
            print(f"   -> ⏭️ Skipped hallucinated garbage filename: '{filename}'")
            continue
        
        save_name = f"UPDATE_{filename}"
        file_path = os.path.join("inbox", save_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"   -> 🔄 Created update file: {save_name}")

# --- THE ORCHESTRATOR ---
def run_pipeline(raw_note_path):
    print(f"🚀 Starting Pipeline for file: {raw_note_path}\n")
    
    if not os.path.exists(raw_note_path):
        print(f"❌ Error: File {raw_note_path} not found.")
        return
        
    db = get_db()
    
    if raw_note_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        process_image(raw_note_path, db)
        print("\n✅ Vision Pipeline completed successfully!")
        return

    with open(raw_note_path, 'r', encoding="utf-8") as f:
        raw_text = f.read()
        
    raw_text = extract_and_solve_embedded_images(raw_text, db)

    existing_context = retrieve_context(raw_text)
    
    # L'AI restituisce ora un dizionario Python pulito
    parsed_json_data = agent_splitter(raw_text, existing_context)
    
    # Python genera i file perfetti
    create_markdown_files(parsed_json_data)
    
    # 3. Creiamo la Literature Note come MOC (Map of Content)
    agent_literature_note(raw_text, raw_note_path, parsed_json_data.get('new_notes', []))
    
    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline("notes/test_rag.md")