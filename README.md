<div align="center">

# 🌌 Cosmind

### Your second brain, mapped like a galaxy.

**A fully local, privacy-first AI knowledge system.** Drop in your messy Markdown notes — Cosmind's multi-agent pipeline turns them into linked atomic notes, lets you _chat_ with your own archive (RAG), and renders the whole thing as a navigable 3D galaxy of ideas.

No cloud required. Your data never leaves your machine.

[![License: MIT](https://img.shields.io/badge/License-MIT-818cf8.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![Local-First](https://img.shields.io/badge/Local--First-Ollama-000000.svg)](https://ollama.com)
[![RAG](https://img.shields.io/badge/RAG-ChromaDB-818cf8.svg)](https://www.trychroma.com)

</div>

---

> [!NOTE]
> **Why Cosmind?** Most "chat with your notes" tools ship your private knowledge to someone else's servers. Cosmind runs the LLM, the embeddings, and the vector store entirely on your hardware (via [Ollama](https://ollama.com) + [ChromaDB](https://www.trychroma.com)). Cloud models are optional, not required.

## ✨ Features

- 🤖 **Multi-agent pipeline** — a team of specialized AI agents (built on [Agno](https://github.com/agno-agi/agno)) processes every note: a *Splitter* breaks text into atomic Zettelkasten notes, a *Researcher* enriches them from the web, a *Vision* agent reads images/screenshots, and a *Lecturer* writes literature-note summaries.
- 🔒 **Privacy-first & local** — runs on Ollama (Qwen2.5, Llama3, Llama3.2-Vision). Set an OpenAI key only if you *want* cloud horsepower.
- 💬 **Chat with your vault (RAG)** — ask questions; answers come **only** from your notes. If the answer isn't there, Cosmind offers to search the web instead.
- 🌌 **3D knowledge galaxy** — explore your ideas in space. PCA for the 3D map, t-SNE for concept "islands", and a cosine-similarity knowledge graph that links related notes automatically.
- 🧠 **Atomic notes + knowledge graph** — auto-generated `derives from` / `leads to` / `similar` links, Obsidian-compatible Markdown frontmatter.
- ✍️ **AI editor copilot** — expand, fact-check, or "explain like a tutor" any selection, with web-cited sources.
- 🖥️ **Web UI + CLI** — a React/TypeScript frontend and FastAPI backend, or a simple terminal control panel.
- 🐳 **Dockerized** — one command to spin up the whole stack.

## 🏛️ Architecture

```
                         ┌───────────────────────────┐
   raw_notes/  ─────────▶│   Multi-Agent Pipeline    │
   (your .md, images)    │   (Agno)                  │
                         │  Splitter · Researcher ·  │
                         │  Vision · Writer ·        │
                         │  Lecturer                 │
                         └────────────┬──────────────┘
                                      │  atomic notes + embeddings
                                      ▼
   ┌─────────────┐          ┌───────────────────┐         ┌────────────────────┐
   │  Ollama /   │◀────────▶│   ChromaDB        │────────▶│  Visualizer        │
   │  OpenAI     │  LLM +   │  (vector store,   │  PCA /  │  3D galaxy · t-SNE │
   │             │  embeds  │   persistent)     │  t-SNE  │  · knowledge graph │
   └─────────────┘          └─────────┬─────────┘         └────────────────────┘
                                      │
                          ┌───────────┴────────────┐
                          │   FastAPI backend      │
                          │   /api/chat · /process │
                          │   /visualize · /vault  │
                          └───────────┬────────────┘
                                      │
                          ┌───────────┴────────────┐
                          │   React + TS frontend  │
                          └────────────────────────┘
```

## 🚀 Quickstart

### Option A — Local (Ollama)

```bash
# 1. Install Ollama and pull a model
ollama pull qwen2.5:14b
ollama pull llama3.2-vision   # for image notes

# 2. Configure
cp .env.example .env          # then edit if needed (LLM_MODEL=qwen2.5:14b)

# 3. Install deps
pip install -r requirements.txt

# 4. Run the control panel
python main.py
```

### Option B — Docker (full stack: API + web UI)

```bash
cp .env.example .env
docker compose up --build
```

Then open the frontend (Vite dev server / served container) and start dropping notes into `raw_notes/`.

### Using cloud models (optional)

Set `OPENAI_API_KEY` in `.env` to route the agents through OpenAI instead of Ollama. Leave it empty to stay 100% local.

```env
# .env
LLM_MODEL=qwen2.5:14b
OPENAI_API_KEY=          # optional — leave blank for fully local
OPENAI_MODEL=gpt-4o-mini # used only if a key is set
```

## 🧭 How to use

Run `python main.py` for the interactive panel:

| Option | What it does |
|--------|--------------|
| 📝 **Process notes** | Ingests `raw_notes/`, splits into atomic notes, links them, indexes into the vector DB |
| 💬 **Chat with brain** | RAG query — answers grounded *only* in your notes, with sources |
| 🌌 **View 3D map** | Generates the interactive galaxy of your knowledge |
| 🔄 **Sync database** | Reconciles the vector DB with the files on disk |

## 🔌 API

The FastAPI backend exposes:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/chat` | RAG query over your vault |
| `POST` | `/api/chat/web-search` | Web-search fallback |
| `POST` | `/api/process` | Run the agent pipeline on `raw_notes/` |
| `GET`  | `/api/visualize` | 3D / 2D / graph data |
| `GET`  | `/api/vault` | Browse indexed chunks |
| `GET`/`POST` | `/api/notes` | List / create notes |
| `POST` | `/api/upload` | Upload images for the vision agent |
| `POST` | `/api/editor/ai` | Editor copilot (expand / validate / tutor) |

## 🛠️ Tech stack

**Python** · [Agno](https://github.com/agno-agi/agno) (agents) · [Ollama](https://ollama.com) · [OpenAI](https://openai.com) · [ChromaDB](https://www.trychroma.com) · scikit-learn (PCA / t-SNE) · FastAPI · **TypeScript** · React + Vite · Docker

## 🗺️ Roadmap

- [ ] Incremental indexing (only re-embed changed notes)
- [ ] Local embedding models (drop the last cloud dependency)
- [ ] Export the knowledge graph to Obsidian Canvas
- [ ] Tests + CI

## 📄 License

[MIT](LICENSE) © 2026 Simone Negro
