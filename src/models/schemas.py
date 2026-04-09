from pydantic import BaseModel, Field # type: ignore

# =======================================================================
# DEFINIZIONE CLASSI STRUTTURATE (PYDANTIC) -> NIENTE PIÙ JSON FRAGILI!
# =======================================================================
class NewNote(BaseModel):
    filename: str = Field(description="Nome del file markdown completo, es. 'concept_name.md'")
    title: str = Field(description="Titolo concettuale")
    aliases: list[str] = Field(description="Alias e sinonimi per questo concetto")
    domain: str = Field(description="Dominio di macro categoria (es. backend, psychology, ai)")
    tldr: str = Field(description="Abstract brevissimo in massimo 2 righe")
    body: str = Field(description="Corpo del testo, rielaborato. Rispetta lo stile e la voce dell'utente!")
    derives_from: list[str] = Field(description="Concetti base da cui deriva")
    leads_to: list[str] = Field(description="Concetti avanzati verso cui porta")
    similar_to: list[str] = Field(description="Concetti trasversali affini")

class NoteUpdate(BaseModel):
    filename: str = Field(description="Il nome esatto del file da aggiornare (es. api_rest.md)")
    content_to_add: str = Field(description="Il testo esatto da appendere in fondo al file")

class ExtractionResult(BaseModel):
    new_notes: list[NewNote] = Field(default=[], description="Lista di note atomiche estratte dall'utente")
    updates: list[NoteUpdate] = Field(default=[], description="Lista di aggiornamenti a file già esistenti nel database")

class ImageAnalysis(BaseModel):
    title: str = Field(description="Titolo dell'immagine")
    description: str = Field(description="Descrizione dettagliata della scena")
    key_concepts: list[str] = Field(description="Elenco di tag o concetti presenti nell'immagine")
    extracted_text: str = Field(description="Testo estrapolato fisicamente dall'immagine")
    summary: str = Field(description="Un brevissimo riassunto di 2/3 righe utile ai fini della RAG")

class NoteDraft(BaseModel):
    title: str
    content: str

class NoteCreate(BaseModel):
    title: str
    content: str