import chromadb # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from sklearn.decomposition import PCA # type: ignore
import textwrap
import os

def visualize_3d_chroma():
    print("🧠 Connessione al Second Brain (ChromaDB)...")
    # Usa il percorso assoluto interno a Docker
    client = chromadb.PersistentClient(path="/app/.chroma_db")
    
    try:
        collection = client.get_collection(name="note_ricerca")
    except Exception:
        print("❌ Collezione 'note_ricerca' non trovata. Hai già processato delle note?")
        return
    
    data = collection.get(include=['embeddings', 'documents', 'metadatas'])
    embeddings = data.get('embeddings')
    
    if embeddings is None or len(embeddings) == 0:
        print("❌ Il database è vuoto. Non c'è nulla da visualizzare.")
        return
        
    print(f"✅ Note trovate: {len(embeddings)}. Elaborazione mappa 3D...")
    
    pca = PCA(n_components=3)
    embeddings_3d = pca.fit_transform(embeddings)
    
    sources = [meta.get('source', 'Sconosciuto') for meta in data['metadatas']]
    hover_texts = ["<br>".join(textwrap.wrap(doc[:150], width=50)) + "..." for doc in data['documents']]

    df = pd.DataFrame({
        'X': embeddings_3d[:, 0],
        'Y': embeddings_3d[:, 1],
        'Z': embeddings_3d[:, 2],
        'File': sources,
        'Contenuto': hover_texts
    })

    fig = px.scatter_3d(
        df, x='X', y='Y', z='Z',
        color='File',
        hover_name='File',
        hover_data={'Contenuto': True, 'X': False, 'Y': False, 'Z': False},
        title="Mappa Semantica 3D del Second Brain",
        template="plotly_dark" # Molto più figo da vedere
    )

    # --- LA MODIFICA È QUI ---
    output_file = "/app/notes/brain_map.html"
    fig.write_html(output_file)
    print(f"\n✨ Mappa generata con successo!")
    print(f"📂 Cerca il file 'brain_map.html' nella cartella 'notes' del tuo progetto Mac e aprilo col browser.")