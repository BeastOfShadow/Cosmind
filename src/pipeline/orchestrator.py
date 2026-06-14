import os
import uuid
import glob
import re
import time
import shutil
from urllib.parse import unquote
from datetime import datetime

import warnings

from src.models.schemas import ExtractionResult, ImageAnalysis
from src.agents.core_agents import vision_agent, splitter_agent, researcher_agent, writer_agent, lecturer_agent
warnings.filterwarnings("ignore", category=UserWarning)


from src.database.vector_db import get_db, sync_notes

os.makedirs("inbox", exist_ok=True)
os.makedirs("notes", exist_ok=True)

print("🧹 Syncing database with local files...")
sync_notes()

# =======================================================================
# SUPPORT FUNCTIONS FOR THE LOCAL DATABASE
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

    # Look up the physical path of the file to save its modification timestamp (mtime)
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
# IMAGE PROCESSING
# =======================================================================

def process_image(filepath, db):
    print(f"\n📸 [Vision Agent] Standalone image analysis: {filepath}")
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
        print(f"✅ Image processed and saved: {note_name}")

    except Exception as e:
        print(f"❌ Image processing error {filepath}: {e}")

def extract_and_solve_embedded_images(content, db):
    # Supports both the standard markdown format ![alt](path) and wikilinks ![[path]]
    regex_wiki = r'!\[\[(.*?\.(?:png|jpg|jpeg|gif|webp))\]\]'
    regex_md = r'!\[.*?\]\((.*?\.(?:png|jpg|jpeg|gif|webp))\)'
    
    matches_wiki = re.findall(regex_wiki, content, re.IGNORECASE)
    matches_md = re.findall(regex_md, content, re.IGNORECASE)
    matches = set(matches_wiki + matches_md)
    
    for match in matches:
        # Get only the file name from the possible full path
        image_name = os.path.basename(match)
        print(f"🔍 [Embedded Vision Agent] Inline image found: {image_name}")
        search_pattern = f"**/{unquote(image_name)}"
        found_files = glob.glob(search_pattern, recursive=True)

        if found_files:
            image_path = found_files[0]
            print(f"✅ Found for indexing: {image_path}")
            try:
                 response = vision_agent.run("Fornisci summary per la ricerca RAG dell'immagine.", images=[image_path])
                 result: ImageAnalysis = response.content

                 print(f"👁️ Image translated into: {result.summary[:50]}...")

                 # INSERT ONLY INTO THE DB FOR SEARCH, DO NOT ALTER THE ORIGINAL MARKDOWN
                 db.add(
                    documents=[result.summary],
                    metadatas=[{"source": match, "type": "embedded_image"}],
                    ids=[f"embedded_{image_name}_analysis"]
                 )
            except Exception as e:
                 print(f"❌ Embedded Image Analysis error: {e}")
        else:
             print(f"❌ Error: Image file not found in the Vault: {image_name}")

    # THE ORIGINAL TEXT IS SACRED - Return the identical content without mutating the Markdown tags
    return content

# =======================================================================
# THE MAIN ORCHESTRA
# =======================================================================

def archive_raw_note(raw_note_path):
    """Move a successfully processed raw note into raw_notes/processed/ so it
    is preserved but no longer picked up by glob('raw_notes/*.md')."""
    if not os.path.exists(raw_note_path):
        return
    archive_dir = os.path.join(os.path.dirname(raw_note_path) or ".", "processed")
    os.makedirs(archive_dir, exist_ok=True)
    dest = os.path.join(archive_dir, os.path.basename(raw_note_path))
    if os.path.exists(dest):
        base, ext = os.path.splitext(os.path.basename(raw_note_path))
        dest = os.path.join(archive_dir, f"{base}_{int(time.time())}{ext}")
    shutil.move(raw_note_path, dest)
    print(f"📦 Archived processed note -> {dest}")


def run_pipeline(raw_note_path):
    """Generator: runs the agent pipeline on a single raw note and yields
    human-readable progress messages (also printed to the Docker logs).
    On success the raw note is moved to raw_notes/processed/."""
    def step(msg):
        print(msg)
        return msg

    yield step(f"🚀 Starting pipeline: {os.path.basename(raw_note_path)}")

    if not os.path.exists(raw_note_path):
        yield step(f"❌ Error: File {raw_note_path} not found.")
        return

    db = get_db()

    if raw_note_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        yield step("📸 Vision Agent: analyzing image...")
        process_image(raw_note_path, db)
        yield step("✅ Vision Pipeline completed successfully!")
        archive_raw_note(raw_note_path)
        return

    with open(raw_note_path, 'r', encoding="utf-8") as f:
        raw_text = f.read()
    raw_text = extract_and_solve_embedded_images(raw_text, db)

    yield step("🔍 Searching the vault for similar notes...")
    existing_context = retrieve_context(raw_text)

    extractor_prompt = f"Contesto vault preesistente:\n{existing_context}\n\nNote odierne dell'utente:\n{raw_text}"
    yield step("🤖 Splitter Agent: extracting atomic notes...")
    extractor_response = splitter_agent.run(extractor_prompt)
    extracted_data: ExtractionResult = extractor_response.content

    oggi = datetime.now()
    data_str = oggi.strftime("%Y-%m-%d")
    id_univoco = oggi.strftime("%Y%m%d%H%M%S")

    total_new = len(extracted_data.new_notes)
    yield step(f"💾 Generating {total_new} atomic note(s)...")

    for i, note in enumerate(extracted_data.new_notes):
        # Strict sanitization for filename and title (replace _ with space)
        safe_title = note.title.replace("_", " ").strip()
        safe_filename = note.filename.replace("_", " ").strip()
        if not safe_filename.endswith('.md'): safe_filename += '.md'

        yield step(f"   => [{i + 1}/{total_new}] Saving atomic note '{safe_title}'")

        # Sacred text, we skip the writer_agent alteration
        expanded_body = note.body.strip()

        # Search only happens if you want to keep the links (which you might want to disable,
        # but we can omit them if the text must be 100% pure. We leave web search out of the body).

        derives = ", ".join([f"[[{x}]]" for x in note.derives_from])
        leads = ", ".join([f"[[{x}]]" for x in note.leads_to])
        similar = ", ".join([f"[[{x}]]" for x in note.similar_to])
        aliases = ", ".join([f'"{x}"' for x in note.aliases])
        
        markdown_content = f"---\nid: {id_univoco}\naliases: [{aliases}]\ntags:\n  - status/1-draft\n  - domain/{note.domain}\ncreated: {data_str}\nmodified: {data_str}\n---\n\n# 📌 {safe_title}\n\n## 🧠 TL;DR\n> [!summary] Abstract\n> {note.tldr}\n\n---\n\n## 📝 Body\n{expanded_body}\n\n---\n\n## 🔗 Knowledge Graph\n- **Derives from:** {derives}\n- **Leads to:** {leads}\n- **Similar:** {similar}\n\n## 📚 Sources\n- User Source Note\n"
        
        file_path = os.path.join("inbox", safe_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"   -> 🆕 Final note saved: {safe_filename}")
        agent_librarian(safe_filename, markdown_content, db)

    for update in extracted_data.updates:
        # Sanitization for Updates too
        fname = update.filename.replace("_", " ").strip()
        if not fname.endswith('.md'):
            fname += '.md'
        content = update.content_to_add.strip()

        # Strict anti-hallucination filter
        if not fname or not content or "string" in fname or "unknown" in fname:
            print(f"   -> ⏭️ Skipped ghost update: '{fname}'")
            continue

        # APPEND mode: adds the file to inbox/ or tries to get it from notes/ (if the user updates existing notes)
        # Here we could create an UPDATE_ file so the user approves the append, or append it directly.
        # We simply edit it safely.
        file_path = os.path.join("inbox", f"UPDATE_{fname}")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## Update {data_str}\n{content}\n")
        print(f"   -> 🔄 Update (Append) saved for: {fname}")

    if extracted_data.new_notes:
        yield step("📑 Lecturer Agent: writing the summary note...")
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

    archive_raw_note(raw_note_path)
    yield step(f"✅ Done: {os.path.basename(raw_note_path)} ({total_new} atomic notes)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for _msg in run_pipeline(sys.argv[1]):
            pass
    else:
        for arg in glob.glob("raw_notes/*.md"):
            for _msg in run_pipeline(arg):
                pass
