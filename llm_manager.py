import os

def get_llm_model(vision=False):
    """
    Ritorna un modello Agno (OpenAIChat o Ollama)
    basato sulla configurazione dell'utente in .env.
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    if OPENAI_API_KEY:
        from agno.models.openai import OpenAIChat
        # Usiamo il cloud (ottimo anche per la vision!)
        return OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    else:
        from agno.models.ollama import Ollama
        # Usiamo il locale
        model_name = os.getenv("LLM_MODEL", "qwen2.5:14b")
        if vision:
            model_name = "llama3.2-vision"
        return Ollama(id=model_name)
