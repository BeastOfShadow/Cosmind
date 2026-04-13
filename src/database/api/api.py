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

# Importiamo dai nostri moduli puliti
from src.models.schemas import EditorAIRequest, NoteCreate
from src.pipeline.orchestrator import run_pipeline
from src.agents.chat_agent import chat_with_brain, chat_with_web
from src.database.visualizer import get_3d_map_data
from src.database.vector_db import sync_notes

app = FastAPI(title="Neural Network Second Brain API", description="API per l'agente RAG e il vault delle note")

# Configurazione CORS per permettere al frontend React (Vite) di comunicare col backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In produzione restringere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve assets folder per le immagini del vault
app.mount("/assets", StaticFiles(directory="notes/assets"), name="assets")

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Second Brain API is running"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    """Esegue una query RAG sulle note del vault"""
    try:
        response = chat_with_brain(request.query)
        if not response:
            return {"answer": "Errore interno durante la RAG", "sources": []}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/web-search")
def chat_web(request: ChatRequest):
    """Esegue una query sul web usando l'agente delegato"""
    try:
        response = chat_with_web(request.query)
        if not response:
            return {"answer": "Errore interno durante la ricerca web", "sources": []}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync")
def sync_database():
    """Sincronizza manualmente ChromaDB con la cartella fisica/inbox"""
    try:
        sync_notes()
        return {"status": "success", "message": "Database sincronizzato con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
def process_inbox():
    """Lancia l'orchestrator per processare tutto ciò che c'è in raw_notes"""
    try:
        note_grezze = glob.glob("raw_notes/*.md")
        if not note_grezze:
            return {"status": "info", "message": "Nessuna nota da processare in 'raw_notes/'."}
            
        for nota in note_grezze:
            run_pipeline(nota)
            
        return {"status": "success", "message": f"{len(note_grezze)} note processate con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visualize")
def get_map_data():
    """Recupera i dati dal database per le mappe 2D, 3D e il Grafo"""
    try:
        return get_3d_map_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault")
def get_vault_contents():
    """Restituisce tutti i chunk salvati nel database per poterli esplorare"""
    try:
        client = chromadb.PersistentClient(path="/app/.chroma_db")
        
        try:
            collection = client.get_collection(name="note_ricerca")
        except Exception:
            return {"documents": [], "total": 0, "error": "Collezione non trovata."}
            
        data = collection.get(include=['metadatas', 'documents'])
        
        if not data or not data.get('documents'):
            return {"documents": [], "total": 0}
            
        docs = []
        for i, doc in enumerate(data['documents']):
            docs.append({
                "id": str(i),
                "source": data['metadatas'][i].get('source', 'Sconosciuto'),
                "preview": doc[:150] + "..." if len(doc) > 150 else doc
            })
            
        return {"documents": docs, "total": len(docs)}
    except Exception as e:
        return {"error": str(e), "documents": [], "total": 0}
    
@app.post("/api/notes")
def save_note(note: NoteCreate):
    """Salva una nuova nota Markdown direttamente nella cartella raw_notes"""
    safe_title = note.title.strip().lower().replace(" ", "_").replace("/", "-")
    if not safe_title:
        safe_title = "nuova_nota"
    
    filename = f"{safe_title}.md"
    target_dir = "raw_notes"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    filepath = os.path.join(target_dir, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {note.title}\n\n{note.content}")
        return {"status": "success", "message": f"Nota salvata in {target_dir}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. ENDPOINT PER LISTARE LE NOTE (GET)
@app.get("/api/notes")
def list_notes():
    """Restituisce la lista dei file Markdown presenti in raw_notes"""
    if not os.path.exists("raw_notes"):
        return {"notes": []}
    
    files = glob.glob("raw_notes/*.md")
    notes = [os.path.basename(f) for f in files]
    return {"notes": notes}

# 4. ENDPOINT PER LEGGERE LA SINGOLA NOTA (GET)
@app.get("/api/notes/{filename}")
def get_note(filename: str):
    """Legge il contenuto di una nota specifica e separa titolo e corpo"""
    filepath = os.path.join("raw_notes", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Nota non trovata")
    
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
    """Carica un'immagine dal frontend alla cartella notes/assets"""
    # Genera nome univoco
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"img_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
    
    notes_assets_dir = "notes/assets"
    if not os.path.exists(notes_assets_dir):
        os.makedirs(notes_assets_dir)
        
    file_location = os.path.join(notes_assets_dir, unique_filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # Restituisce la sintassi Markdown in base all'estensione
    if ext.lower() == ".pdf":
        md_syntax = f"[Documento PDF](assets/{unique_filename})\n"
    else:
        md_syntax = f"![Immagine caricata](assets/{unique_filename})\n"
        
    return {
        "info": f"File salvato come {unique_filename}",
        "markdown_syntax": md_syntax
    }

@app.delete("/api/upload/{filename}")
def delete_file(filename: str):
    """Elimina un file dalla cartella assets"""
    file_location = os.path.join("notes/assets", filename)
    if os.path.exists(file_location):
        os.remove(file_location)
        return {"status": "success", "message": f"File {filename} eliminato"}
    raise HTTPException(status_code=404, detail="File non trovato")

@app.post("/api/editor/ai")
def editor_ai_assistant(request: EditorAIRequest):
    try:
        testo = request.text
        azione = request.action
        
        print(f"🤖 Avvio AI Copilot per azione: {azione}")

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
            return {"result": f"❌ Azione sconosciuta: {azione}"}

        # Creiamo l'agente
        editor_agent = Agent(
            name="Editor Copilot",
            role=ruolo,
            model=get_llm_model(),
            tools=usa_tools,
            instructions=istruzioni
        )
        
        # Eseguiamo la richiesta
        prompt = f"Analizza questo testo e svolgi il tuo compito:\n\n{testo}"
        risposta = editor_agent.run(prompt)
        
        # Se tutto va bene, ritorniamo il testo dell'AI
        return {"result": risposta.content.strip()}

    except Exception as e:
        # Se qualcosa si rompe, stampiamo l'errore nel terminale di Docker
        import traceback
        traceback.print_exc()
        
        # Invece di far crollare FastAPI (che causa il finto errore CORS),
        # restituiamo l'errore al frontend come se fosse la risposta dell'AI!
        return {"result": f"❌ Errore interno del sistema: {str(e)}"}