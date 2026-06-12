import chromadb # type: ignore
from sklearn.decomposition import PCA # type: ignore
from sklearn.manifold import TSNE # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import textwrap

def get_3d_map_data():
    print("🧠 Retrieving data from the Second Brain for the Analytics Dashboard...")
    client = chromadb.PersistentClient(path="/app/.chroma_db")

    try:
        collection = client.get_collection(name="note_ricerca")
    except Exception:
        return {"error": "Collection not found. The database is empty."}

    data = collection.get(include=['embeddings', 'documents', 'metadatas'])
    embeddings = data.get('embeddings')

    if embeddings is None or len(embeddings) < 2:
        return {"error": "The database is empty or has too little data to generate charts."}

    # 1. 3D computation (PCA) for fast spatial visualization
    pca_3d = PCA(n_components=3)
    emb_3d = pca_3d.fit_transform(embeddings)

    # 2. 2D computation (t-SNE) to form concept "islands"
    # We handle perplexity safely in case there are few notes
    perplex = min(30, len(embeddings) - 1)
    tsne_2d = TSNE(n_components=2, perplexity=perplex, random_state=42)
    emb_2d = tsne_2d.fit_transform(embeddings)

    # 3. Knowledge Graph computation (Similarity Matrix)
    sim_matrix = cosine_similarity(embeddings)

    traces_3d = {}
    traces_2d = {}
    nodes = []
    links = []

    # Populate the nodes and the spatial traces
    for i, meta in enumerate(data['metadatas']):
        source = meta.get('source', 'Unknown')
        testo = data['documents'][i]
        hover_text = "<br>".join(textwrap.wrap(testo[:100], width=40)) + "..."

        # Structure for 3D Map
        if source not in traces_3d:
            traces_3d[source] = {"x": [], "y": [], "z": [], "texts": [], "name": source}
        traces_3d[source]["x"].append(float(emb_3d[i, 0]))
        traces_3d[source]["y"].append(float(emb_3d[i, 1]))
        traces_3d[source]["z"].append(float(emb_3d[i, 2]))
        traces_3d[source]["texts"].append(source)

        # Structure for 2D t-SNE Map
        if source not in traces_2d:
            traces_2d[source] = {"x": [], "y": [], "texts": [], "name": source}
        traces_2d[source]["x"].append(float(emb_2d[i, 0]))
        traces_2d[source]["y"].append(float(emb_2d[i, 1]))
        traces_2d[source]["texts"].append(hover_text)

        # Nodes for the Graph
        nodes.append({
            "id": str(i),
            "name": source,
            "val": 1, # Node size
            "preview": testo[:100] + "..."
        })

    # Populate the graph links: connect nodes with similarity > 75%
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = float(sim_matrix[i, j])
            if similarity > 0.75: # Correlation threshold! Change it to get more or fewer lines
                links.append({"source": str(i), "target": str(j), "similarity": similarity})

    return {
        "traces3D": list(traces_3d.values()),
        "traces2D": list(traces_2d.values()),
        "graph": {"nodes": nodes, "links": links}
    }