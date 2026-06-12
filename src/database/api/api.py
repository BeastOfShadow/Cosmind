from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File # type: ignore
import shutil
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel # type: ignore
import glob
import chromadb # type: ignore
import os
from agno.agent import Agent # type: ignore
from agno.tools.duckduckgo import DuckDuckGoTools # type: ignore
from src.config.llm_manager import get_llm_model

# Import from our clean modules
from src.models.schemas import EditorAIRequest, NoteCreate
from src.pipeline.orchestrator import run_pipeline
from src.agents.chat_agent import chat_with_brain, chat_with_web
from src.database.visualizer import get_3d_map_data
from src.database.vector_db import sync_notes

app = FastAPI(title="Neural Network Cosmind API", description="API for the RAG agent and the notes vault")

# CORS configuration to allow the React frontend (Vite) to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve assets folder for the vault images
app.mount("/assets", StaticFiles(directory="notes/assets"), name="assets")

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Cosmind API is running"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    """Runs a RAG query over the vault notes"""
    try:
        response = chat_with_brain(request.query)
        if not response:
            return {"answer": "Internal error during RAG", "sources": []}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/web-search")
def chat_web(request: ChatRequest):
    """Runs a query on the web using the delegated agent"""
    try:
        response = chat_with_web(request.query)
        if not response:
            return {"answer": "Internal error during web search", "sources": []}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync")
def sync_database():
    """Manually syncs ChromaDB with the physical/inbox folder"""
    try:
        sync_notes()
        return {"status": "success", "message": "Database synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
def process_inbox():
    """Launches the orchestrator to process everything in raw_notes"""
    try:
        note_grezze = glob.glob("raw_notes/*.md")
        if not note_grezze:
            return {"status": "info", "message": "No notes to process in 'raw_notes/'."}

        for nota in note_grezze:
            run_pipeline(nota)

        return {"status": "success", "message": f"{len(note_grezze)} notes processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visualize")
def get_map_data():
    """Retrieves data from the database for the 2D, 3D maps and the Graph"""
    try:
        return get_3d_map_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault")
def get_vault_contents():
    """Returns all the chunks saved in the database so they can be explored"""
    try:
        client = chromadb.PersistentClient(path="/app/.chroma_db")

        try:
            collection = client.get_collection(name="note_ricerca")
        except Exception:
            return {"documents": [], "total": 0, "error": "Collection not found."}
            
        data = collection.get(include=['metadatas', 'documents'])
        
        if not data or not data.get('documents'):
            return {"documents": [], "total": 0}
            
        docs = []
        for i, doc in enumerate(data['documents']):
            docs.append({
                "id": str(i),
                "source": data['metadatas'][i].get('source', 'Unknown'),
                "preview": doc[:150] + "..." if len(doc) > 150 else doc
            })
            
        return {"documents": docs, "total": len(docs)}
    except Exception as e:
        return {"error": str(e), "documents": [], "total": 0}
    
@app.post("/api/notes")
def save_note(note: NoteCreate):
    """Saves a new Markdown note directly into the raw_notes folder"""
    safe_title = note.title.strip().lower().replace(" ", "_").replace("/", "-")
    if not safe_title:
        safe_title = "untitled_note"
    
    filename = f"{safe_title}.md"
    target_dir = "raw_notes"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    filepath = os.path.join(target_dir, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {note.title}\n\n{note.content}")
        return {"status": "success", "message": f"Note saved to {target_dir}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. ENDPOINT TO LIST NOTES (GET)
@app.get("/api/notes")
def list_notes():
    """Returns the list of Markdown files present in raw_notes"""
    if not os.path.exists("raw_notes"):
        return {"notes": []}
    
    files = glob.glob("raw_notes/*.md")
    notes = [os.path.basename(f) for f in files]
    return {"notes": notes}

# 4. ENDPOINT TO READ A SINGLE NOTE (GET)
@app.get("/api/notes/{filename}")
def get_note(filename: str):
    """Reads the content of a specific note and separates title and body"""
    filepath = os.path.join("raw_notes", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Note not found")
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split('\n')
    title = ""
    body = content
    
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = '\n'.join(lines[1:]).strip()
        
    return {"title": title, "content": body}

import time
import uuid

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads an image from the frontend to the notes/assets folder"""
    # Generate a unique name
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"img_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
    
    notes_assets_dir = "notes/assets"
    if not os.path.exists(notes_assets_dir):
        os.makedirs(notes_assets_dir)
        
    file_location = os.path.join(notes_assets_dir, unique_filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # Returns the Markdown syntax based on the extension
    if ext.lower() == ".pdf":
        md_syntax = f"[PDF Document](assets/{unique_filename})\n"
    else:
        md_syntax = f"![Uploaded image](assets/{unique_filename})\n"

    return {
        "info": f"File saved as {unique_filename}",
        "markdown_syntax": md_syntax
    }

@app.delete("/api/upload/{filename}")
def delete_file(filename: str):
    """Deletes a file from the assets folder"""
    file_location = os.path.join("notes/assets", filename)
    if os.path.exists(file_location):
        os.remove(file_location)
        return {"status": "success", "message": f"File {filename} deleted"}
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/editor/ai")
def editor_ai_assistant(request: EditorAIRequest):
    try:
        testo = request.text
        azione = request.action
        
        print(f"🤖 Starting AI Copilot for action: {azione}")

        if azione == "expand":
            ruolo = "Ricercatore"
            istruzioni = [
                "Usa DuckDuckGo per cercare concetti correlati e sviluppi recenti.",
                "Includi sempre i link delle fonti alla fine.",
                "Usa il Markdown."
            ]
            usa_tools = [DuckDuckGoTools()]
            
        elif azione == "validate":
            ruolo = "Fact-Checker"
            istruzioni = [
                "Verifica sul web se le affermazioni fatte in questo testo sono corrette.",
                "Correggi le inesattezze e cita sempre le fonti (URL).",
                "Usa il Markdown."
            ]
            usa_tools = [DuckDuckGoTools()]
            
        elif azione == "tutor":
            ruolo = "Tutor"
            istruzioni = [
                "Agisci come un professore empatico.",
                "Spiega i concetti complessi in modo semplice e fai esempi pratici.",
                "Usa il Markdown."
            ]
            usa_tools = []
        else:
            return {"result": f"❌ Unknown action: {azione}"}

        # Create the agent
        editor_agent = Agent(
            name="Editor Copilot",
            role=ruolo,
            model=get_llm_model(),
            tools=usa_tools,
            instructions=istruzioni
        )
        
        # Run the request
        prompt = f"Analizza questo testo e svolgi il tuo compito:\n\n{testo}"
        risposta = editor_agent.run(prompt)

        # If everything goes well, return the AI text
        return {"result": risposta.content.strip()}

    except Exception as e:
        # If something breaks, print the error in the Docker terminal
        import traceback
        traceback.print_exc()

        # Instead of crashing FastAPI (which causes the fake CORS error),
        # return the error to the frontend as if it were the AI's response!
        return {"result": f"❌ Internal system error: {str(e)}"}