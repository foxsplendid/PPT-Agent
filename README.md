English | [中文](README.zh.md)

# Paper PPT Agent

> Upload an academic paper, and a multi-agent AI pipeline turns it into an editable, high-fidelity presentation.

## Overview

Paper PPT Agent is a multi-agent tool that converts academic papers (PDF / TeX) into editable PowerPoint presentations. A FastAPI backend orchestrates a Strategist → Executor → Critic agent pipeline that parses the paper, plans the deck, generates SVG slides, and compiles them to PPTX; a React + Vue (PPTist) frontend provides a workbench for uploading papers, watching live progress, refining results, and editing slides before export.

This is a **research-group private-use fork** of the upstream open-source project [CRui5in/paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) (forked from the May 2026 commit `0c5d9f6`). It adds deep customizations for real lab workflows: one-click task resume, LaTeX formula rendering, MinerU ingestion with local fallback, LLM streaming with gateway-timeout hardening, and extra model-provider support.

## Features

- **Multi-agent pipeline** — Strategist → Executor → Critic stages collaborate to extract content, plan the deck, generate SVG slides, and self-review the visual output.
- **One-click resume** *(custom)* — When an Agent job stops mid-run (e.g. a Cloudflare `524` timeout or a hard-stop for review), `POST /generate/{job_id}/resume` continues it in place from its workspace instead of starting over.
- **LaTeX formula rendering** *(custom)* — `latex_render.py` extracts math and chemical formulas from the paper and renders them to high-fidelity PNGs embedded directly in the slides.
- **MinerU ingestion with fallback** *(custom)* — Uses the MinerU PDF engine to rebuild double-column reading order and parse tables to HTML, with automatic fallback to local PyMuPDF text extraction when MinerU is unavailable.
- **LLM streaming & timeout defense** *(custom)* — Chunk-based streaming and bounded timeouts prevent long-context papers from hanging on gateway timeouts.
- **Multi-model providers** — OpenAI, Anthropic, Gemini, plus relay aggregators and Xiaomi MiMo (`xiaomi`) via the LLM registry and `.env` configuration.
- **Feedback & iteration** — Target-page or full regeneration, agent feedback/interrupt, version snapshots, and history.
- **Visual PPT editor** — A PPTist-based editor (Vue) embedded in the React frontend for adjusting text, notes, and fonts before export.
- **RAG icon matching** — Semantic icon search (Gemini embeddings + BM25) to match icons to slide content.
- **Deep Research enrichment** — Optional external lookups via arXiv / Semantic Scholar with relevance filtering.

## Installation

Requirements:

| Dependency | Version |
| :--- | :--- |
| Python | 3.11–3.12 |
| [uv](https://docs.astral.sh/uv/) | latest |
| Node.js / npm | 18+ |

The backend is managed with `uv` (see `pyproject.toml` / `uv.lock`); the frontend uses Vite (see `frontend/package.json`).

```bash
git clone https://github.com/foxsplendid/PPT-Agent.git
cd PPT-Agent

# Backend dependencies (locked)
uv sync --locked

# Frontend dependencies
cd frontend && npm install && cd ..
```

Configuration: copy `.env.example` to `.env` and fill in at least one provider key. Supported keys include `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, and `XIAOMI_API_KEY` / `XIAOMI_BASE_URL`. Optional: `MINERU_API_KEY` / `MINERU_API_URL` for high-fidelity PDF parsing, and `IMAGE_BACKEND` for image generation. `DEFAULT_LLM_PROVIDER` and `DEFAULT_LLM_MODEL` select the default model.

## Usage

One-command start (installs deps, launches both services, opens the browser):

```bash
# Windows
.\start-dev.bat

# Linux / macOS
sh start-dev.sh
```

Both scripts run `python -m backend.dev_launcher`, which starts the Vite frontend (default port `5173`) and the Uvicorn backend (default port `8000`, auto-selecting a free port if taken; override with the `BACKEND_PORT` env var) and opens the workbench.

Manual start:

```bash
# Backend (FastAPI app entrypoint is backend/app.py -> app)
uv run python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload --reload-dir backend

# Frontend
cd frontend
npm run dev
```

Run tests:

```bash
uv run pytest   # config in pytest.ini, tests under tests/
```

## Project Structure

```
PPT-Agent/
├── backend/                 # FastAPI backend (package built via hatchling)
│   ├── app.py               # FastAPI application entrypoint (app)
│   ├── dev_launcher.py      # Spawns frontend + backend dev servers, opens browser
│   ├── config.py            # Settings (.env-driven)
│   ├── api/endpoints/       # REST routes: generate, refine, upload, download, session, ...
│   ├── orchestrator/        # Multi-agent pipeline (strategist, svg_executor, svg_critic, research)
│   ├── parser/              # Paper ingestion: mineru_parser, pdf_parser, latex_parser, equation_renderer
│   ├── generator/           # SVG→PPTX compile, font/sanitize, visual_critic, template import
│   ├── llm/                 # Provider registry (openai / anthropic / gemini) + retry
│   ├── queue/ workers/      # Job queue (huey) and generation workers
│   └── session/            # Session manager and progress tracking
├── frontend/                # React 19 + Vite app
│   └── src/pptist/          # Embedded PPTist (Vue) visual editor
├── assets/
│   ├── agent_skills/        # Agent skill definitions (paper-ppt-generate / -research / -deep-research)
│   │   └── paper-ppt-generate/scripts/latex_render.py   # LaTeX → PNG render pipeline
│   ├── icons/ templates/    # Icon library and slide layout/chart templates
├── scripts/build_icon_index.py   # Build the RAG icon search index
├── start-dev.bat / start-dev.sh  # One-command dev launch
├── pyproject.toml / uv.lock      # Backend deps (uv)
└── LICENSE                       # AGPL-3.0
```

## Status

Active, research-group private-use fork at version `0.1.0` (backend and frontend), kept in sync with upstream `CRui5in/paper-ppt-agent` (latest merge of `upstream/master`). Customizations are tracked separately from the upstream baseline.

## License

Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE). Any deployment, distribution, or network service must comply with the AGPL-3.0 terms.

## Acknowledgements

- [paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) — upstream project this fork is derived from.
- [PPTAgent](https://github.com/icip-cas/PPTAgent) — pipeline and multi-agent design reference.
- [ppt-master](https://github.com/hugohe3/ppt-master) — PPTX compiler implementation reference.
- [PPTist](https://github.com/pipipi-pikachu/PPTist) — embedded visual editor.
