import os
import uuid
import glob
import re
from urllib.parse import unquote
from datetime import datetime

import warnings

from src.models.schemas import ExtractionResult, ImageAnalysis
from src.agents.core_agents import vision_agent, splitter_agent, researcher_agent, writer_agent, lecturer_agent
warnings.filterwarnings("ignore", category=UserWarning)


from src.database.vector_db import get_db, sync_notes

os.makedirs("inbox", exist_ok=True)
os.makedirs("notes", exist_ok=True)

print("🧹 Syncing Database con file locali...")
sync_notes()

# =======================================================================
# FUNZIONI DI SUPPORTO PER IL DATABASE LOCALE
# =======================================================================

def retrieve_context(raw_text):
    print("🔍 Local RAG: Searching the Vector DB for existing similar notes...")
    collection = get_db()
    try:
        results = collection.query(query_texts=[raw_text], n_results=3)
        if results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
            sources = results['metadatas'][0]
            context = ""
            for doc, meta in zip(docs, sources):
                context += f"\n### EXISTING NOTE: {meta['source']}\n{doc}\n"
            print("   -> Existing context found.")
            return context
    except Exception:
        print("   -> DB is empty or still initializing.")
    return "No existing notes found in the database."

def agent_librarian(filename, content, db):
    print(f"📚 Librarian: Indexing {filename} into the Vector DB...")
    
    # Cerca il percorso fisico del file per salvarne il timestamp di modifica (mtime)
    file_path = os.path.join("inbox", filename)
    if not os.path.exists(file_path):
        file_path = os.path.join("notes", filename)
        
    mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
    
    db.add(
        documents=[content],
        metadatas=[{"source": filename, "mtime": mtime}],
        ids=[str(uuid.uuid4())]
    )

# =======================================================================
# TRATTAMENTO IMMAGINI
# =======================================================================

def process_image(filepath, db):
    print(f"\n📸 [Vision Agent] Analisi immagine autonoma: {filepath}")
    try:
        response = vision_agent.run("Analizza l'immagine nel dettaglio.", images=[filepath])
        result: ImageAnalysis = response.content
        
        base_name = os.path.basename(filepath)
        note_name = f"image_note_{base_name}.md"
        out_path = os.path.join("notes", note_name)
        
        markdown_content = f"---\ntags:\n  - status/1-draft\n  - image\ntitle: {result.title}\nkey_concepts: {', '.join(result.key_concepts)}\n---\n\n![[{base_name}]]\n\n# {result.title}\n\n## 🖼️ Descrizione\n{result.description}\n\n## 📝 Testo Estratto\n> {result.extracted_text if result.extracted_text else 'Nessun testo rivelato.'}\n"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        db.add(
            documents=[result.summary],
            metadatas=[{"source": note_name, "type": "image_analysis"}],
            ids=[f"{base_name}_analysis"]
        )
        print(f"✅ Immagine processata e salvata: {note_name}")
        
    except Exception as e:
        print(f"❌ Errore processamento immagine {filepath}: {e}")

def extract_and_solve_embedded_images(content, db):
    # Supporta sia il formato standard markdown ![alt](path) che i wikilink ![[path]]
    regex_wiki = r'!\[\[(.*?\.(?:png|jpg|jpeg|gif|webp))\]\]'
    regex_md = r'!\[.*?\]\((.*?\.(?:png|jpg|jpeg|gif|webp))\)'
    
    matches_wiki = re.findall(regex_wiki, content, re.IGNORECASE)
    matches_md = re.findall(regex_md, content, re.IGNORECASE)
    matches = set(matches_wiki + matches_md)
    
    for match in matches:
        # Recupera solo il nome del file dall'eventuale path completo
        image_name = os.path.basename(match)
        print(f"🔍 [Embedded Vision Agent] Immagine inline trovata: {image_name}")
        search_pattern = f"**/{unquote(image_name)}"
        found_files = glob.glob(search_pattern, recursive=True)
        
        if found_files:
            image_path = found_files[0]
            print(f"✅ Ritrovata per indicizzazione: {image_path}")
            try:
                 response = vision_agent.run("Fornisci summary per la ricerca RAG dell'immagine.", images=[image_path])
                 result: ImageAnalysis = response.content
                 
                 print(f"👁️ Immagine tradotta in: {result.summary[:50]}...")
                 
                 # INSERISCI SOLO NEL DB PER LA RICERCA, NON ALTERARE IL MARKDOWN ORIGINALE
                 db.add(
                    documents=[result.summary],
                    metadatas=[{"source": match, "type": "embedded_image"}],
                    ids=[f"embedded_{image_name}_analysis"]
                 )
            except Exception as e:
                 print(f"❌ Errore Analisi Immagine Embedded: {e}")
        else:
             print(f"❌ Errore: File immagine non trovato nel Vault: {image_name}")
            
    # IL TESTO ORIGINALE È SACRO - Ritorniamo il content identico senza mutare i tag Markdown
    return content

# =======================================================================
# L'ORCHESTRA PRINCIPALE
# =======================================================================

def run_pipeline(raw_note_path):
    print(f"🚀 Starting Agno Pipeline for file: {raw_note_path}\n")
    
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
    
    extractor_prompt = f"Contesto vault preesistente:\n{existing_context}\n\nNote odierne dell'utente:\n{raw_text}"
    print("🤖 Splitter Agent in esecuzione...")
    extractor_response = splitter_agent.run(extractor_prompt)
    extracted_data: ExtractionResult = extractor_response.content
    
    oggi = datetime.now()
    data_str = oggi.strftime("%Y-%m-%d")
    id_univoco = oggi.strftime("%Y%m%d%H%M%S")
    
    print("💾 Python Formatter & Researchers: Generazione delle Atomic Notes...")
    
    for i, note in enumerate(extracted_data.new_notes):
        # Sanitizzazione rigorosa per filename e titolo (sostituisci _ con spazio)
        safe_title = note.title.replace("_", " ").strip()
        safe_filename = note.filename.replace("_", " ").strip()
        if not safe_filename.endswith('.md'): safe_filename += '.md'
        
        print(f"   => Salvataggio Atomic Note '{safe_title}'")
        
        # Testo sacro, saltiamo l'alterazione del writer_agent
        expanded_body = note.body.strip()
        
        # La ricerca avviene solo se si vuole conservare i link (che potresti voler disattivare, 
        # ma possiamo ometterli se il testo deve essere 100% puro. Lasciamo web search out dal body).
        
        derives = ", ".join([f"[[{x}]]" for x in note.derives_from])
        leads = ", ".join([f"[[{x}]]" for x in note.leads_to])
        similar = ", ".join([f"[[{x}]]" for x in note.similar_to])
        aliases = ", ".join([f'"{x}"' for x in note.aliases])
        
        markdown_content = f"---\nid: {id_univoco}\naliases: [{aliases}]\ntags:\n  - status/1-draft\n  - domain/{note.domain}\ncreated: {data_str}\nmodified: {data_str}\n---\n\n# 📌 {safe_title}\n\n## 🧠 TL;DR\n> [!summary] Abstract\n> {note.tldr}\n\n---\n\n## 📝 Body\n{expanded_body}\n\n---\n\n## 🔗 Knowledge Graph\n- **Derives from:** {derives}\n- **Leads to:** {leads}\n- **Similar:** {similar}\n\n## 📚 Sources\n- User Source Note\n"
        
        file_path = os.path.join("inbox", safe_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"   -> 🆕 Salvata nota finale: {safe_filename}")
        agent_librarian(safe_filename, markdown_content, db)
        
    for update in extracted_data.updates:
        # Sanitizzazione anche per gli Updates
        fname = update.filename.replace("_", " ").strip()
        if not fname.endswith('.md'):
            fname += '.md'
        content = update.content_to_add.strip()
        
        # Filtro rigoroso anti-allucinazione
        if not fname or not content or "string" in fname or "unknown" in fname:
            print(f"   -> ⏭️ Skipped ghost update: '{fname}'")
            continue
            
        # Modalità APPEND: aggiunge il file a inbox/ o tenta di prenderlo da notes/ (se l'utente aggiorna note preesistenti)
        # Qui potremmo creare un file UPDATE_ in modo che l'utente approvi l'append, o accodarlo direttamente. 
        # Modifichiamo semplicemente in modo sicuro.
        file_path = os.path.join("inbox", f"UPDATE_{fname}")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## Update {data_str}\n{content}\n")
        print(f"   -> 🔄 Update (Append) salvato per: {fname}")

    if extracted_data.new_notes:
        print("📑 Lecturer Agent: Generazione MOC riassuntiva...")
        try:
            lecturer_resp = lecturer_agent.run(raw_text)
            summary = lecturer_resp.content.strip()
        except:
             summary = "Nessun riassunto."
             
        links_markdown = "\n".join([f"- [[{note.filename.replace('.md', '')}]] - *{note.title}*" for note in extracted_data.new_notes])
        
        lit_filename = f"LIT_{os.path.basename(raw_note_path)}"
        markdown_content = f"---\nid: {id_univoco}\ntags:\n  - type/literature-note\n  - status/1-draft\ncreated: {data_str}\nmodified: {data_str}\n---\n\n# 📚 source: {os.path.basename(raw_note_path)}\n\n## 📝 Summary\n{summary}\n\n---\n\n## 🔗 Atomic Concepts Extracted\n{links_markdown}\n"
        
        file_path = os.path.join("inbox", lit_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"   -> 🆕 Generated Literature Note: {lit_filename}")
        agent_librarian(lit_filename, markdown_content, db)

    print("\n✅ Agno Orchestration Pipeline completed successfully!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        for arg in glob.glob("raw_notes/*.md"):
            run_pipeline(arg)
