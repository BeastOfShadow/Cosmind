import chromadb # type: ignore
from sklearn.decomposition import PCA # type: ignore
from sklearn.manifold import TSNE # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import textwrap

def get_3d_map_data():
    print("🧠 Recupero dati dal Second Brain per Dashboard Analitica...")
    client = chromadb.PersistentClient(path="/app/.chroma_db")
    
    try:
        collection = client.get_collection(name="note_ricerca")
    except Exception:
        return {"error": "Collezione non trovata. Il database è vuoto."}
    
    data = collection.get(include=['embeddings', 'documents', 'metadatas'])
    embeddings = data.get('embeddings')
    
    if embeddings is None or len(embeddings) < 2:
        return {"error": "Il database è vuoto o ha troppo pochi dati per generare grafici."}
        
    # 1. Calcolo 3D (PCA) per la visualizzazione spaziale veloce
    pca_3d = PCA(n_components=3)
    emb_3d = pca_3d.fit_transform(embeddings)
    
    # 2. Calcolo 2D (t-SNE) per formare "isole" di concetti
    # Gestiamo la perplexity in modo sicuro nel caso ci siano poche note
    perplex = min(30, len(embeddings) - 1)
    tsne_2d = TSNE(n_components=2, perplexity=perplex, random_state=42)
    emb_2d = tsne_2d.fit_transform(embeddings)

    # 3. Calcolo del Grafo di Conoscenza (Matrice di Somiglianza)
    sim_matrix = cosine_similarity(embeddings)
    
    traces_3d = {}
    traces_2d = {}
    nodes = []
    links = []

    # Popoliamo i nodi e le tracce spaziali
    for i, meta in enumerate(data['metadatas']):
        source = meta.get('source', 'Sconosciuto')
        testo = data['documents'][i]
        hover_text = "<br>".join(textwrap.wrap(testo[:100], width=40)) + "..."
        
        # Struttura per Mappa 3D
        if source not in traces_3d:
            traces_3d[source] = {"x": [], "y": [], "z": [], "texts": [], "name": source}
        traces_3d[source]["x"].append(float(emb_3d[i, 0]))
        traces_3d[source]["y"].append(float(emb_3d[i, 1]))
        traces_3d[source]["z"].append(float(emb_3d[i, 2]))
        traces_3d[source]["texts"].append(source)
        
        # Struttura per Mappa 2D t-SNE
        if source not in traces_2d:
            traces_2d[source] = {"x": [], "y": [], "texts": [], "name": source}
        traces_2d[source]["x"].append(float(emb_2d[i, 0]))
        traces_2d[source]["y"].append(float(emb_2d[i, 1]))
        traces_2d[source]["texts"].append(hover_text)

        # Nodi per il Grafo
        nodes.append({
            "id": str(i),
            "name": source,
            "val": 1, # Dimensione del nodo
            "preview": testo[:100] + "..."
        })

    # Popoliamo i link del grafo: colleghiamo i nodi con somiglianza > 75%
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = float(sim_matrix[i, j])
            if similarity > 0.75: # Soglia di correlazione! Modificala per avere più o meno linee
                links.append({"source": str(i), "target": str(j), "similarity": similarity})

    return {
        "traces3D": list(traces_3d.values()),
        "traces2D": list(traces_2d.values()),
        "graph": {"nodes": nodes, "links": links}
    }