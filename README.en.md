# Paper PPT Agent (Research Group Private Use Edition)

<p align="center">
  <b>Upload an academic paper, AI automatically generates high-fidelity presentations</b>
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="AGPL-3.0 License"></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/uv-powered-DE5FE9?logo=astral&logoColor=white" alt="uv">
</p>

<p align="center">
  <a href="./README.md">中文</a> | English
</p>

---

> [!IMPORTANT]
> **📢 Research Group Private Use Statement**  
> This project is an enhanced and customized edition of the open-source multi-agent presentation generator, designed for **private research group use**.  
> It is derived from the upstream repository [CRui5in/paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) (based on the May 2026 commit version `0c5d9f6`), and has been optimized for academic paper parsing and presentation compilation workflows under our custom multi-model relay environments.

---

## 🛠️ Custom Enhanced Features for Research Group

Compared to the upstream version, this customized edition integrates the following core technical modules:

1.  **Task Pausing and One-Click Resume (Resume Workflow)**
    *   Integrates session persistence within the backend pipeline. When a generation task is interrupted by LLM fluctuations or triggers human audit (Hard-Stop), a one-click `Resume` button is provided on the frontend. By requesting `POST /generate/{job_id}/resume`, the task resumes **in-place** without starting over, saving both time and Tokens.
2.  **High-Fidelity LaTeX Scientific Formula Rendering Pipeline**
    *   Adds a dedicated [latex_render.py](file:///D:/Code/Jupyter/PPT-Agent/assets/agent_skills/paper-ppt-generate/scripts/latex_render.py) compilation pipeline to the skill generator. It automatically extracts LaTeX formulas and chemical equations from the paper body and renders them into high-fidelity PNG images for embedding in the PPTX pages, resolving math alignment and corruption issues in academic presentations.
3.  **High-Accuracy PDF Ingestion (MinerU Integration & Fallback)**
    *   Integrates the [MinerU](https://github.com/opendatalab/MinerU) PDF parsing engine to reconstruct double-column layouts and parse complex tables into clean HTML. Includes a **resilient fallback defense**: if the MinerU API experiences fluctuations or timeouts, it automatically downgrades to local `PyMuPDF` text extraction, ensuring 24/7 service availability.
4.  **LLM Streaming Output & 524 Gateway Timeout Defense**
    *   Upgrades the LLM connection layer to support chunk-based Stream outputs, and locks down reasonable timeout bounds. This completely prevents the system from hanging or crashing due to Cloudflare `524` timeouts during long paper processing.
5.  **Multi-Model Relay & Custom Provider Adaptations**
    *   Adds support for the OpenAI-Next API aggregator and Xiaomi MiMo provider in the LLM registry. It also corrects `.env` configuration priorities to ensure environment variables are correctly injected into the Vite frontend and Uvicorn backend subprocesses.

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **Multi-Agent Pipeline** | Strategist $\rightarrow$ Executor $\rightarrow$ Critic three-stage collaboration for content extraction and layout generation. |
| **Task Resume & Recovery** | *[Custom]* One-click resume after task pausing, preventing timeouts and saving Tokens. |
| **LaTeX Formula Rendering** | *[Custom]* Automatically renders LaTeX math formulas into high-fidelity inline PNGs with clean layouts. |
| **MinerU PDF Ingestion** | *[Custom]* Reconstructs reading order for double-column papers and converts tables to HTML with PyMuPDF fallback. |
| **Feedback Iteration** | Target-page or full regeneration with structural changes, version history, and snapshot diffs. |
| **PPT Web Editor** | Built-in PPTist-based visual editor to adjust text, notes, fonts, and slides before exporting. |
| **RAG Icon Matching** | Semantic search via Gemini Embedding to automatically match icons to slide content. |
| **Deep Research** | External research enhancement (arXiv / Semantic Scholar / Web) with automatic relevance filtering. |

---

## ⚙️ Requirements

| Dependency | Minimum Version |
| :--- | :--- |
| 🐍 Python | 3.11+ |
| 📦 [uv](https://docs. Astral.sh/uv/) | latest |
| 🟢 Node.js | 18+ |

*   **API Configuration**: Create a `.env` file in the root folder. Supports OpenAI / Anthropic / Gemini / DeepSeek API keys, or custom aggregator base URLs (e.g., OpenAI-Next).
*   **LaTeX Rendering**: The formula rendering pipeline requires basic local matplotlib installation and related scientific package dependencies.

---

## 🚀 Quick Start

```bash
# Clone the research group customized repository
git clone https://github.com/foxsplendid/PPT-Agent.git
cd PPT-Agent

# One-click start (automatically install dependencies and run services in background)
# Windows
.\start-dev.bat
# Linux
sh start-dev.sh
```

*   **Service Endpoints**:
    *   **Frontend Workbench**: [http://127.0.0.1:5174](http://127.0.0.1:5174)
    *   **Backend API Service**: [http://127.0.0.1:8100](http://127.0.0.1:8100)

*(Note: Compared to the upstream default configurations, this version uses port `5174` for the frontend and `8100` for the backend to prevent port collisions on local machines.)*

<details>
<summary>📎 Manual Start Instructions</summary>

```bash
# Backend installation and startup
uv sync --locked
uv run python -m uvicorn backend.app:app --host 127.0.0.1 --port 8100 --reload --reload-dir backend

# Frontend installation and startup
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

</details>

---

## 📋 Changelog (Research Group Custom Track)

### June 2026 (Research Group Custom Release)
*   🧠 **One-Click Resume Task Recovery** — Introduced pipeline pause and resume features.
*   🔬 **LaTeX Formula Rendering Pipeline** — Generates high-fidelity formulas as slide images.
*   🔍 **MinerU Parser Integration & Fallback** — Added parser support for complex double-column academic papers.
*   📡 **LLM Streaming Rewrite** — Greatly reduces LLM request gateway timeouts.
*   ⚙️ **Multi-Model Support & Port Isolation** — Integrated OpenAI-Next aggregator, Xiaomi MiMo, and isolated ports (`5174` frontend / `8100` backend).

---

## 🙏 Acknowledgements

*   [paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) — This project is directly derived from this upstream open-source project. Many thanks to the original author for the excellent framework.
*   [PPTAgent](https://github.com/icip-cas/PPTAgent) — Reference for pipeline design and multi-agent coordination.
*   [ppt-master](https://github.com/hugohe3/ppt-master) — Reference for the PPTX compiler implementation.
*   [PPTist](https://github.com/pipipi-pikachu/PPTist) — Integrated editor reference.

---

## 📄 License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE). Any deployment or commercial usage must comply with the AGPL-3.0 terms.
