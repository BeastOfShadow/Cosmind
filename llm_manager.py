import os
import base64
import ollama

def encode_image_base64(image_path):
    """Verifica e converte un'immagine in Base64 (Standard per le API)"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"⚠️ Impossibile leggere immagine '{image_path}': {e}")
        return None

def ask_llm(prompt, require_json=False, image_paths=None):
    """
    Invia un prompt al modello, opzionalmente con un array di file path immagini.
    Se in locale, usa llava/llama3.2-vision automaticamente (fallback).
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")
    
    # Se passano immagini, forziamo un modello vision in locale
    if image_paths:
        LLM_MODEL = "llama3.2-vision" 

    # 1. Usa prima OpenAI se configurato
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # OpenAI accetta un array misto object per testo e immagini
            if image_paths:
                content_array = [{"type": "text", "text": prompt}]
                for img_path in image_paths:
                    base64_image = encode_image_base64(img_path)
                    if base64_image:
                        content_array.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        })
                messages = [{'role': 'user', 'content': content_array}]
            else:
                messages = [{'role': 'user', 'content': prompt}]
            
            kwargs = {'model': OPENAI_MODEL, 'messages': messages}
            if require_json:
                kwargs['response_format'] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except ImportError:
            print("⚠️ Hai configurato OPENAI_API_KEY ma manca la libreria 'openai'. Faccio fallback su Ollama...")
        except Exception as e:
            print(f"⚠️ Errore OpenAI ({e}). Fallback su Ollama locale...")
    
    # 2. Fallback su locale (Ollama)
    try:
        messages = [{'role': 'user', 'content': prompt}]
        # Ollama accetta direttemente i percorsi base64 (o array di file locali visti dall'app locale) nel dizionario
        if image_paths:
             messages[0]['images'] = image_paths
             
        kwargs = {'model': LLM_MODEL, 'messages': messages}
        
        if require_json:
            kwargs['format'] = 'json'
            
        print(f"🧠 Avvio Ollama Locale su modello: {LLM_MODEL}...")    
        response = ollama.chat(**kwargs)
        return response['message']['content']
    except Exception as e:
        print(f"❌ Errore critico: Modello locale ({LLM_MODEL}) non accessibile. Dettagli: {e}")
        raise RuntimeError("Impossibile connettersi all'API AI. Controlla che Ollama sia acceso e se hai scaricato il modello vision (`ollama pull llama3.2-vision`).")