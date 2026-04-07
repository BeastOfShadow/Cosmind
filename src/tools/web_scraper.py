import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

def read_webpage(url: str) -> str:
    """Legge e restituisce il contenuto testuale di una pagina web."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return text[:3000] # Limitiamo a 3000 caratteri per non sovraccaricare il modello
    except Exception as e:
        return f"Impossibile leggere la pagina {url}: {e}"