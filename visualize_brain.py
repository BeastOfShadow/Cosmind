import chromadb
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
import textwrap

def visualize_3d_chroma():
    print("🧠 Connessione al Second Brain (ChromaDB)...")
    # Connettiti allo stesso database usato dal tuo manager
    client = chromadb.PersistentClient(path="./.chroma_db")
    collection = client.get_collection(name="note_ricerca")
    
    # Estrai TUTTO: ID, metadati, testo e soprattutto i Vettori (Embeddings)
    data = collection.get(include=['embeddings', 'documents', 'metadatas'])
    
    embeddings = data.get('embeddings')
    if not embeddings:
        print("❌ Nessun vettore (embedding) trovato nel database.")
        return
        
    print(f"✅ Trovate {len(embeddings)} note vettorializzate. Compressione in 3D in corso...")
    
    # 1. Riduzione della dimensionalità da ~384 dimensioni a 3 (PCA)
    pca = PCA(n_components=3)
    embeddings_3d = pca.fit_transform(embeddings)
    
    # 2. Prepariamo i dati per il grafico
    sources = []
    hover_texts = []
    
    for i in range(len(embeddings)):
        # Estrai il nome del file dal metadato "source"
        meta = data['metadatas'][i]
        source_name = meta.get('source', 'Sconosciuto') if meta else 'Sconosciuto'
        sources.append(source_name)
        
        # Prendi un pezzetto di testo per mostrarlo quando passi col mouse sul pallino
        doc = data['documents'][i]
        # Taglia e va a capo per non avere una riga chilometrica nel tooltip
        short_doc = "<br>".join(textwrap.wrap(doc[:150], width=50)) + "..."
        hover_texts.append(short_doc)

    # 3. Creiamo un DataFrame Pandas (comodo per Plotly)
    df = pd.DataFrame({
        'X': embeddings_3d[:, 0],
        'Y': embeddings_3d[:, 1],
        'Z': embeddings_3d[:, 2],
        'File': sources,
        'Contenuto': hover_texts
    })

    # 4. Generiamo il Grafico 3D
    print("🌌 Generazione dell'universo 3D...")
    fig = px.scatter_3d(
        df, x='X', y='Y', z='Z',
        color='File', # Colora i pallini in base al file di origine
        hover_name='File',
        hover_data={'Contenuto': True, 'X': False, 'Y': False, 'Z': False},
        title="Mappa Semantica 3D del Second Brain",
        opacity=0.8
    )
    
    # Migliora lo stile visivo
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, b=0, t=40))
    
    # Mostra il grafico nel browser
    fig.show()

if __name__ == "__main__":
    visualize_3d_chroma()