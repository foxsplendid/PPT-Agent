# Paper PPT Agent (课题组自用定制版)

<p align="center">
  <b>上传学术论文，多智能体自动生成高保真演示文稿</b>
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
  中文 | <a href="./README.en.md">English</a>
</p>

---

> [!IMPORTANT]
> **📢 课题组自用声明**  
> 本项目是基于开源多智能体项目进行定制与增强的**课题组自用**学术论文演示文稿（PPT）自动生成工具。  
> 本版本派生自上游开源仓库 [CRui5in/paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent)（基于 2026年5月提交版本 `0c5d9f6`），并根据课题组在实际科研汇报、组会展示及多模型中转环境下的真实需求，进行了多项底层的深度定制与功能加固。

---

## 🛠️ 课题组专属定制增强特性

相比上游原始版本，本定制版累计新增并优化了以下核心技术模块：

1.  **任务暂停与一键恢复 (Resume 工作流)**
    *   在后端管道引入了会话持久化保护，当任务遭遇大模型响应中断或触发人工审核（Hard-Stop）时，前端工作台提供一键 `Resume` 按钮，通过 `POST /generate/{job_id}/resume` 直接**原地续跑**，无需从头重新生成，极大地保护了长任务的执行连贯性并节省 Token。
2.  **LaTeX 学术公式高精度渲染管线**
    *   在 PPT 技能生成模块中，独创性地合入了 [latex_render.py](file:///D:/Code/Jupyter/PPT-Agent/assets/agent_skills/paper-ppt-generate/scripts/latex_render.py) 编译管线，能自动提取正文中的数学公式、化学式并转换为高保真 PNG 图片原生嵌入幻灯片，彻底解决学术 PPT 复杂的公式排版乱码痛点。
3.  **高精度 Ingestion 摄取（MinerU 接入与本地降级）**
    *   集成了新一代 [MinerU](https://github.com/opendatalab/MinerU) PDF 解析引擎，自动重构双栏阅读顺序并提取高还原度 HTML 表格。同时设计了**自动降级（Fallback）**防御，在 MinerU service 波动或无网时，优雅回退至本地 `PyMuPDF` 纯文本提取，确保系统全天候高可用。
4.  **大模型流式输出与 524 超时防御**
    *   将 LLM 交互逻辑升级为 Stream 块流式接收，并在底层锁定了合理的 LLM 超时边界，完全解决了官方版面对长上下文论文时容易因为 API 响应过慢导致 Cloudflare 网关返回 `524` 错误导致任务彻底挂起的漏洞。
5.  **多模型中继与自定义服务商适配**
    *   在模型注册表和底层驱动中，接入了对第三方中继聚合器（OpenAI-Next）以及小米 MiMo 大模型的适配支持；同时修正了本地 `.env` 环境变量的优先级，使其能无损注入到 Vite 前端及 Uvicorn 后端子进程。

---

## ✨ 功能亮点

| 功能 | 说明 |
| :--- | :--- |
| **多智能体流水线** | Strategist $\rightarrow$ Executor $\rightarrow$ Critic 三阶段协作，内容提炼与版式生成一体化。 |
| **任务续跑恢复** | *[定制]* 支持生成阻断后一键恢复（Resume），防超时与中断，高度省 Token。 |
| **高保真公式渲染** | *[定制]* 学术 LaTeX 公式自动转 PNG 矢量高精图，直接生成优雅排版。 |
| **MinerU 高精摄取** | *[定制]* 双栏论文阅读序重构，无框线表格转 HTML 原生组件，带 PyMuPDF 自动降级。 |
| **反馈迭代** | 指定单页或全量重生成，支持结构调整，自动版本快照与历史回溯。 |
| **PPT 编辑器** | 内置基于 PPTist 深度定制的可视化编辑器，支持结果页直接调整文字、备注、字体并快速导出。 |
| **RAG 图标匹配** | 基于 Gemini Embedding 的 RAG 语义搜索，自动匹配最合适的幻灯片小图标。 |
| **Deep Research** | 外部科研研究增强（arXiv / Semantic Scholar / Web），相关性自动过滤。 |

---

## ⚙️ 环境要求

| 依赖 | 最低版本要求 |
| :--- | :--- |
| 🐍 Python | 3.11+ |
| 📦 [uv](https://docs.astral.sh/uv/) | latest |
| 🟢 Node.js | 18+ |

*   **API 密钥配置**：在根目录下创建并配置 `.env` 文件。支持官方 OpenAI / Anthropic / Gemini / DeepSeek 密钥，或者自定义中继代理 API（如 OpenAI-Next）。
*   **LaTeX 渲染依赖**：使用公式渲染管线需要本地安装好基本的 matplotlib 以及相关的科学计算库依赖。

---

## 🚀 快速开始

```bash
# 克隆课题组自用定制仓库
git clone https://github.com/foxsplendid/PPT-Agent.git
cd PPT-Agent

# 一键启动（自动安装依赖并后台挂载前后端服务）
# Windows
.\start-dev.bat
# Linux
sh start-dev.sh
```

*   **服务访问入口**：
    *   **前端工作台**：[http://127.0.0.1:5174](http://127.0.0.1:5174)
    *   **后端 API 服务**：[http://127.0.0.1:8100](http://127.0.0.1:8100)

*(注：相比官方默认端口，本版本已将前端调整为 `5174`，后端调整为 `8100`，以防止与本地其他正在运行的交互服务冲突。)*

<details>
<summary>📎 手动分步启动说明</summary>

```bash
# 后端安装依赖并启动
uv sync --locked
uv run python -m uvicorn backend.app:app --host 127.0.0.1 --port 8100 --reload --reload-dir backend

# 前端安装依赖并启动
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

</details>

---

## 📋 更新日志（课题组演进记录）

### 2026 年 6 月 (课题组定制强化版)
*   🧠 **一键 Resume 任务恢复机制** — 引入任务暂停与状态重续。
*   🔬 **LaTeX 公式渲染管线** — 高保真将公式渲染为幻灯片内 PNG 图片。
*   🔍 **MinerU 解析器与自动 Fallback** — 支持对复杂 PDF 论文的高解析度 Ingestion。
*   📡 **大模型 Streaming 改写** — 大幅减低 LLM 请求超时挂起的风险。
*   ⚙️ **多模型服务商与端口隔离** — 扩充 OpenAI-Next 聚合器、小米 MiMo，隔离前端（5174）与后端（8100）端口。

---

## 🙏 参考项目

*   [paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) — 本项目直接派生自该上游开源项目。感谢原作者的优秀框架设计。
*   [PPTAgent](https://github.com/icip-cas/PPTAgent) — 流程设计与 Agent 多智能体协作架构参考。
*   [ppt-master](https://github.com/hugohe3/ppt-master) — 部分底层 PPTX 编译器工程实现参考。
*   [PPTist](https://github.com/pipipi-pikachu/PPTist) — Web 可视化编辑器集成参考。

---

## 📄 许可证

本项目基于 [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE) 发布。在使用、分发或提供网络服务时，必须严格遵守 AGPL-3.0 协议的相关规定。
