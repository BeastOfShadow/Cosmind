from agno.agent import Agent # type: ignore
from agno.tools.duckduckgo import DuckDuckGoTools # type: ignore
from src.config.llm_manager import get_llm_model
from src.models.schemas import ExtractionResult, ImageAnalysis
from src.tools.web_scraper import read_webpage # type: ignore

# =======================================================================
# GLI AGENTI AGNO - SQUADRA AL COMPLETO
# =======================================================================

splitter_agent = Agent(
    name="Data Extractor",
    role="Estrattore di Conoscenza Zettelkasten",
    model=get_llm_model(),
    output_schema=ExtractionResult,
    instructions=[
        "Riceverai gli appunti grezzi dell'utente e il contesto preesistente nel Vault.",
        "Se l'utente parla di concetti del tutto nuovi, definisci oggetti 'NewNote'.",
        "Assicurati che i filename e i title contengano nomi validi e parlanti.",
        "Il campo body DEVE contenere il succo di tutto, rispettando il tone of voice dell'utente.",
        "Genera un output fedele allo schema."
    ]
)

# 2. Potenziamo il Researcher Agent passandogli lo strumento
researcher_agent = Agent(
    name="Deep Researcher",
    role="Cercare e leggere documenti accademici e tecnici sul web",
    model=get_llm_model(),
    tools=[DuckDuckGoTools(), read_webpage],
    instructions=[
        "1. Usa DuckDuckGo per cercare l'argomento (prediligi documentazione ufficiale o paper).",
        "2. USA SEMPRE lo strumento 'read_webpage' per leggere il contenuto reale dei primi 2 link utili trovati.",
        "3. Sintetizza il testo che hai letto dalle pagine web, scartando banner, cookie, o informazioni non pertinenti.",
        "4. Restituisci la sintesi tecnica e i link che hai visitato."
    ]
)

writer_agent = Agent(
    name="Synthesizer Editor",
    role="Autore di Note Zettelkasten",
    model=get_llm_model(),
    instructions=[
        "Il tuo compito è espandere l'appunto base dell'utente incrociandolo col contesto web cercato dal ricercatore.",
        "NON usare la voce da assistente IA. Usa la voce originaria dell'utente.",
        "Consegna esclusivamente testo formattato in puro Markdown pronto da copia-incollare.",
    ]
)

lecturer_agent = Agent(
    name="Map of Content Creator",
    role="Bibliotecario MOC",
    model=get_llm_model(),
    instructions=[
        "L'utente ha elaborato svariati concetti. Scrivi una 'Literature Note'.",
        "Ritorna un riassunto coeso e discorsivo dei punti trattati e dei takeaway principali.",
        "Evita introduzioni come 'Ecco il riassunto'. Ritorna direttamente il testo in markdown."
    ]
)

vision_agent = Agent(
    name="Vision Analyst",
    role="Analista di Immagini e Screenshot",
    model=get_llm_model(vision=True),
    output_schema=ImageAnalysis,
    instructions=[
        "Sei gli occhi del Second Brain.",
        "Analizza l'immagine fornita estraendone testo, significato e contesto generale.",
        "Restituisci l'oggetto strutturato con i campi richiesti in modo che l'Orchestratore possa indicizzare la conoscenza."
    ]
)