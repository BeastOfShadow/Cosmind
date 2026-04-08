# 🧠 Second Brain AI: Neural Network Agent

Welcome to your **Second Brain AI**. This project transforms a chaotic folder of Markdown notes and files into an intelligent, searchable, and 3D-visualized knowledge ecosystem.

The system leverages AI agents (via **Agno**) to analyze your notes, extract atomic concepts, and allow you to "chat" with your personal archive using **RAG** (Retrieval-Augmented Generation).

## 🚀 Key Features

* **Intelligent Pipeline**: Processes raw notes, cleans them, extracts tags, and creates linked atomic notes.
* **Privacy-First (Local)**: Native support for **Ollama** (Qwen2.5, Llama3, etc.) for total data privacy.
* **Hybrid Cloud**: Option to use **OpenAI (GPT-4o)** for higher speed or more complex reasoning.
* **Vector Database**: Persistent semantic memory management via **ChromaDB**.
* **3D Semantic Map**: Interactive visualization of your note "galaxy" based on content similarity.
* **Dockerized**: Fully isolated environment to prevent dependency conflicts and ensure easy setup.

---

## 📂 Project Structure

```text
my_second_brain/
├── src/                      # ⚙️ The Engine (Source Code)
│   ├── agents/               # AI Agents (Chat, Librarian, etc.)
│   ├── config/               # LLM Management & Settings
│   ├── database/             # ChromaDB logic & 3D Visualizer
│   └── pipeline/             # Data flow orchestrator
├── inbox/                    # 📥 Processed & Literature Notes
├── notes/                    # 📚 Final Vault (Atomic Notes)
├── raw_notes/                # 📝 Entry point for raw files
├── .chroma_db/               # 🗄️ Vector Database (Persistent)
├── main.py                   # 🎛️ Interactive Control Panel
├── start.sh                  # 🚀 Boot script & Model setup
└── run.sh                    # 💻 Daily usage script
```

---

## 🛠️ Requirements

* **Docker** & **Docker Compose**.
* **Ollama** (if running models locally).
* An internet connection (only for initial model downloads or if using OpenAI).

---

## 🏗️ Installation & Setup

1.  **Configure Environment**: Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_key_here_if_applicable
    LLM_MODEL=qwen2.5:14b
    ```

2.  **Set Permissions**:
    ```bash
    chmod +x start.sh run.sh
    ```

3.  **Initialize the System**:
    ```bash
    ./start.sh
    ```
    *This script checks your API keys, pulls required Ollama models, and builds the Docker container.*

---

## 📖 How to Use

To interact with your Second Brain, simply use the main command:

```bash
./run.sh
```

You will see an interactive menu with the following options:
1.  **📝 Process Notes**: Ingests files from `raw_notes`, analyzes them with AI, and saves atomic notes to `inbox`.
2.  **💬 Chat with Brain**: Query your vault. The AI responds based *only* on your personal data.
3.  **🌌 View 3D Map**: Generates a `brain_map.html` file to explore your concepts visually.
4.  **🔄 Sync Database**: Cleans the DB by removing references to files you have manually deleted.

---

## 🧠 Technical Highlights

* **Persistence**: ChromaDB data is stored in a Docker volume (`chroma_data`), keeping your index safe even if the container is destroyed.
* **RAG (Retrieval-Augmented Generation)**: When querying, the system retrieves the most relevant snippets from your vault and provides them as context to the LLM.
* **Visualization**: The visualizer uses **PCA** (Principal Component Analysis) to compress high-dimensional AI vectors into a navigable 3D space.

---

## 📝 License
Developed for personal knowledge optimization and research workflows.
