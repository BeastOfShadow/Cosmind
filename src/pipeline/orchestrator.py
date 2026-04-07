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


from src.database.vector_db import get_db, sync_deleted_notes

os.makedirs("inbox", exist_ok=True)
os.makedirs("notes", exist_ok=True)

print("🧹 Syncing Database con file locali...")
sync_deleted_notes()

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
    db.add(
        documents=[content],
        metadatas=[{"source": filename}],
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
    regex = r'!\[\[(.*?\.(?:png|jpg|jpeg|gif|webp))\]\]'
    matches = re.findall(regex, content, re.IGNORECASE)
    
    for match in matches:
        print(f"🔍 [Embedded Vision Agent] Immagine inline trovata: ![[{match}]]")
        search_pattern = f"**/{unquote(match)}"
        found_files = glob.glob(search_pattern, recursive=True)
        
        if found_files:
            image_path = found_files[0]
            print(f"✅ Ritrovata: {image_path}")
            try:
                 response = vision_agent.run("Fornisci summary per la ricerca RAG dell'immagine.", images=[image_path])
                 result: ImageAnalysis = response.content
                 
                 print(f"👁️ Immagine tradotta in: {result.summary[:50]}...")
                 
                 content = content.replace(f"![[{match}]]", f"![[{match}]]\n\n> [Vision Analysis]: {result.summary}")
                 
                 db.add(
                    documents=[result.summary],
                    metadatas=[{"source": match, "type": "embedded_image"}],
                    ids=[f"embedded_{match}_analysis"]
                 )
            except Exception as e:
                 print(f"❌ Errore Analisi Immagine Embedded: {e}")
        else:
             print(f"❌ Errore: File immagine non trovato nel Vault: {match}")
            
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
        print(f"   => Elaborazione approfondita per '{note.title}'")
        
        research_response = researcher_agent.run(f"Cerca approfondimenti tecnici o documenti per il concetto '{note.title}' (dominio: {note.domain})")
        scraped_context = research_response.content
        
        write_prompt = f"""Sei un Technical Writer esperto. Riscrivi ed espandi l'appunto dell'utente.
        
        REGOLA CRITICA E ASSOLUTA: Questo concetto appartiene strettamente al dominio: '{note.domain}'. 
        Se la ricerca web parla di argomenti fuori da questo dominio (es. filosofia, grammatica, dibattiti sociali, forum in altre lingue), IGNORALA COMPLETAMENTE.
        Usa la ricerca web SOLO se aggiunge valore tecnico e accademico all'appunto dell'utente.
        Restituisci solo il Markdown pulito, senza presentazioni.
        
        TESTO GREZZO DELL'UTENTE:
        {note.body}
        
        RICERCA WEB UTILE:
        {scraped_context}
        """
        try:
            writer_response = writer_agent.run(write_prompt)
            expanded_body = writer_response.content.strip()
        except:
            expanded_body = note.body
            
        derives = ", ".join([f"[[{x}]]" for x in note.derives_from])
        leads = ", ".join([f"[[{x}]]" for x in note.leads_to])
        similar = ", ".join([f"[[{x}]]" for x in note.similar_to])
        aliases = ", ".join([f'"{x}"' for x in note.aliases])
        
        markdown_content = f"---\nid: {id_univoco}\naliases: [{aliases}]\ntags:\n  - status/1-draft\n  - domain/{note.domain}\ncreated: {data_str}\nmodified: {data_str}\n---\n\n# 📌 {note.title}\n\n## 🧠 TL;DR\n> [!summary] Abstract\n> {note.tldr}\n\n---\n\n## 📝 Body\n{expanded_body}\n\n---\n\n## 🔗 Knowledge Graph\n- **Derives from:** {derives}\n- **Leads to:** {leads}\n- **Similar:** {similar}\n\n## 📚 Sources\n- User Notes & Agent Web Search\n"
        
        # FIX: Assicurati che l'estensione .md sia sempre presente
        note_filename = note.filename.strip()
        if not note_filename.endswith('.md'):
            note_filename += '.md'
            
        file_path = os.path.join("inbox", note_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"   -> 🆕 Salvata nota finale: {note_filename}")
        agent_librarian(note_filename, markdown_content, db)
        
    for update in extracted_data.updates:
        fname = update.filename.strip()
        if not fname.endswith('.md'):
            fname += '.md'
        content = update.content_to_add.strip()
        
        # Filtro rigoroso anti-allucinazione
        if not fname or not content or "string" in fname or "unknown" in fname:
            print(f"   -> ⏭️ Skipped ghost update: '{fname}'")
            continue
            
        file_path = os.path.join("inbox", f"UPDATE_{fname}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   -> 🔄 Update salvato per: {fname}")

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
