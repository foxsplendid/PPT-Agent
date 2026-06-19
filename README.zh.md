[English](README.md) | 中文

# Paper PPT Agent

> 上传学术论文，多智能体 AI 流水线自动生成可编辑、高保真的演示文稿。

## 概述

Paper PPT Agent 是一个多智能体工具，可将学术论文（PDF / TeX）转换为可编辑的 PowerPoint 演示文稿。后端基于 FastAPI，编排 Strategist → Executor → Critic 三阶段智能体流水线：解析论文、规划页面结构、生成 SVG 幻灯片并编译为 PPTX；前端基于 React，并内嵌 Vue 版 PPTist 编辑器，提供上传论文、实时查看进度、反馈重生成以及导出前可视化编辑的工作台。

本仓库是上游开源项目 [CRui5in/paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) 的**课题组自用定制分支**（派生自 2026 年 5 月提交版本 `0c5d9f6`）。针对真实科研汇报场景做了多项深度定制：一键任务续跑、LaTeX 公式渲染、MinerU 摄取与本地降级、LLM 流式输出与网关超时加固，以及更多模型服务商支持。

## 功能特性

- **多智能体流水线** — Strategist → Executor → Critic 三阶段协作，完成内容提炼、页面规划、SVG 幻灯片生成与视觉自审。
- **一键续跑** *(定制)* — 当 Agent 任务中途中断（如 Cloudflare `524` 超时或触发人工审核 Hard-Stop）时，通过 `POST /generate/{job_id}/resume` 基于工作区原地续跑，无需从头重来。
- **LaTeX 公式渲染** *(定制)* — `latex_render.py` 从论文正文提取数学公式与化学式，渲染为高保真 PNG 并直接嵌入幻灯片。
- **MinerU 摄取与降级** *(定制)* — 使用 MinerU PDF 引擎重建双栏阅读顺序、将表格解析为 HTML；MinerU 不可用时自动降级到本地 PyMuPDF 纯文本提取。
- **LLM 流式与超时防御** *(定制)* — 分块流式接收并锁定合理超时边界，避免长上下文论文因网关超时而挂起。
- **多模型服务商** — 通过 LLM 注册表与 `.env` 配置支持 OpenAI、Anthropic、Gemini，以及第三方中转聚合器与小米 MiMo（`xiaomi`）。
- **反馈与迭代** — 单页或全量重生成、Agent 反馈/打断、版本快照与历史回溯。
- **可视化 PPT 编辑器** — 在 React 前端内嵌的 PPTist（Vue）编辑器，可在导出前调整文字、备注与字体。
- **RAG 图标匹配** — 基于 Gemini Embedding + BM25 的语义图标检索，为幻灯片内容自动匹配图标。
- **Deep Research 增强** — 可选地通过 arXiv / Semantic Scholar 进行外部检索，并做相关性过滤。

## 安装

环境要求：

| 依赖 | 版本 |
| :--- | :--- |
| Python | 3.11–3.12 |
| [uv](https://docs.astral.sh/uv/) | 最新版 |
| Node.js / npm | 18+ |

后端使用 `uv` 管理依赖（见 `pyproject.toml` / `uv.lock`），前端使用 Vite（见 `frontend/package.json`）。

```bash
git clone https://github.com/foxsplendid/PPT-Agent.git
cd PPT-Agent

# 安装后端依赖（锁定版本）
uv sync --locked

# 安装前端依赖
cd frontend && npm install && cd ..
```

配置：将 `.env.example` 复制为 `.env`，并至少填入一个服务商密钥。支持的密钥包括 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`GEMINI_API_KEY`、`DEEPSEEK_API_KEY`，以及 `XIAOMI_API_KEY` / `XIAOMI_BASE_URL`。可选项：`MINERU_API_KEY` / `MINERU_API_URL` 用于高保真 PDF 解析，`IMAGE_BACKEND` 用于图像生成。`DEFAULT_LLM_PROVIDER` 与 `DEFAULT_LLM_MODEL` 用于指定默认模型。

## 使用方法

一键启动（自动安装依赖、启动前后端服务并打开浏览器）：

```bash
# Windows
.\start-dev.bat

# Linux / macOS
sh start-dev.sh
```

两个脚本都会运行 `python -m backend.dev_launcher`，它启动 Vite 前端（默认端口 `5173`）与 Uvicorn 后端（默认端口 `8000`，若被占用则自动选择空闲端口，可用 `BACKEND_PORT` 环境变量覆盖），并打开工作台。

手动启动：

```bash
# 后端（FastAPI 入口为 backend/app.py -> app）
uv run python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload --reload-dir backend

# 前端
cd frontend
npm run dev
```

运行测试：

```bash
uv run pytest   # 配置见 pytest.ini，测试位于 tests/
```

## 项目结构

```
PPT-Agent/
├── backend/                 # FastAPI 后端（通过 hatchling 构建为包）
│   ├── app.py               # FastAPI 应用入口（app）
│   ├── dev_launcher.py      # 拉起前后端开发服务并打开浏览器
│   ├── config.py            # 配置（由 .env 驱动）
│   ├── api/endpoints/       # REST 路由：generate、refine、upload、download、session 等
│   ├── orchestrator/        # 多智能体流水线（strategist、svg_executor、svg_critic、research）
│   ├── parser/              # 论文摄取：mineru_parser、pdf_parser、latex_parser、equation_renderer
│   ├── generator/           # SVG→PPTX 编译、字体/清洗、visual_critic、模板导入
│   ├── llm/                 # 服务商注册表（openai / anthropic / gemini）与重试
│   ├── queue/ workers/      # 任务队列（huey）与生成 worker
│   └── session/            # 会话管理与进度追踪
├── frontend/                # React 19 + Vite 前端
│   └── src/pptist/          # 内嵌 PPTist（Vue）可视化编辑器
├── assets/
│   ├── agent_skills/        # 智能体技能定义（paper-ppt-generate / -research / -deep-research）
│   │   └── paper-ppt-generate/scripts/latex_render.py   # LaTeX → PNG 渲染管线
│   ├── icons/ templates/    # 图标库与幻灯片版式/图表模板
├── scripts/build_icon_index.py   # 构建 RAG 图标检索索引
├── start-dev.bat / start-dev.sh  # 一键启动开发环境
├── pyproject.toml / uv.lock      # 后端依赖（uv）
└── LICENSE                       # AGPL-3.0
```

## 状态

处于活跃维护中，为课题组自用定制分支，版本 `0.1.0`（前后端一致），与上游 `CRui5in/paper-ppt-agent` 保持同步（已合并最新的 `upstream/master`）。定制内容与上游基线分开维护。

## 许可证

基于 [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE) 发布。任何部署、分发或提供网络服务都必须遵守 AGPL-3.0 协议条款。

## 致谢

- [paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) — 本分支派生自该上游项目。
- [PPTAgent](https://github.com/icip-cas/PPTAgent) — 流水线与多智能体协作设计参考。
- [ppt-master](https://github.com/hugohe3/ppt-master) — PPTX 编译器实现参考。
- [PPTist](https://github.com/pipipi-pikachu/PPTist) — 内嵌可视化编辑器。
