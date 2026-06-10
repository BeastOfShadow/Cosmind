# Contributing to Cosmind

Thanks for your interest in Cosmind — a local-first, privacy AI second brain. Contributions of every size are welcome, from typo fixes to new agents.

## Ways to contribute

- 🐛 **Report a bug** — open an issue with steps to reproduce, your OS, and which model/runtime you used (Ollama model name or OpenAI).
- 💡 **Suggest a feature** — open an issue describing the use case. Check the [Roadmap](README.md#-roadmap) first.
- 📝 **Improve docs** — README, this file, or inline comments. Docs PRs are always welcome and a great first contribution.
- 🔧 **Send a fix or feature** — see the workflow below.

Good first areas (see the roadmap): local embedding models, incremental re-indexing, chunking long notes before embedding, and tests.

## Dev setup

Cosmind is **Python** (agents, pipeline, API) + **TypeScript/React** (frontend).

```bash
# 1. Fork & clone
git clone https://github.com/<you>/Cosmind.git
cd Cosmind

# 2. Python deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Local model (privacy-first default)
ollama pull qwen2.5:14b
ollama pull llama3.2-vision

# 4. Config
cp .env.example .env

# 5. Run
python main.py                 # CLI control panel
# or the full stack:
docker compose up --build
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Workflow

1. **Open an issue first** for anything non-trivial, so we can agree on the approach before you write code.
2. Branch from `main`: `git checkout -b feat/short-description`.
3. Keep PRs focused — one logical change per PR.
4. Write a clear PR description: what changed, why, and how you tested it.
5. Make sure the app still runs (`python main.py`, and `docker compose up` if you touched the stack).

## Code style

- **Python**: follow PEP 8. Keep functions small and named for what they do.
- **Comments & user-facing strings**: English, so the project stays accessible to all contributors.
- **No secrets in commits**: `.env` is gitignored — never commit API keys. Your notes (`inbox/`, `notes/`, `raw_notes/`) and `.chroma_db/` are gitignored too; keep private data out of the repo.
- Match the style of the surrounding code.

## Reporting security issues

Please **do not** open a public issue for security problems. Email the maintainer instead: simonenegro.dev@gmail.com.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers the project.
