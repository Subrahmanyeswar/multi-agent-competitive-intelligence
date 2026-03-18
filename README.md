# Multi-Agent Competitive Intelligence System

> An autonomous AI-powered competitive intelligence platform that continuously monitors competitor activity, performs strategic analysis, and generates professional weekly reports — all triggered from a clean dashboard.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?style=flat-square&logo=react)
![Mistral AI](https://img.shields.io/badge/LLM-Mistral%20AI-orange?style=flat-square)
![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## What It Does

This system deploys a crew of specialized AI agents that work together to produce a competitive intelligence report on demand. Click one button — the agents scrape the web, analyze the data, and deliver a structured PDF report with SWOT analysis, weak signal detection, and strategic recommendations.

**Tracked competitors (configurable):** OpenAI · Google DeepMind · Meta AI

---

## Live Demo — Dashboard Pages

| Page | Description |
|---|---|
| **Dashboard** | Live stats — articles collected, signals detected, vectors stored, run history |
| **Live Pipeline** | Animated 6-stage pipeline visualizer with real-time log terminal |
| **Agent Activity** | All 5 agents with roles, tools, status, and last activity timestamps |
| **Intelligence** | Per-company SWOT analysis, sentiment momentum, signal velocity chart |
| **Signal Graph** | D3 force-directed network graph of companies, topics, and signal relationships |
| **Reports** | PDF download, inline report preview, SWOT summary, key developments |
| **Data Store** | All collected articles, vector DB stats, search and filter |

---

## System Architecture
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard (Port 8000)               │
│         Dashboard · Pipeline · Intelligence · Reports        │
└────────────────────────┬────────────────────────────────────┘
│ HTTP / REST API
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Server (api_server.py)             │
│         /api/run · /api/status · /api/signals · /api/report  │
└──────┬──────────────────┬──────────────────┬───────────────-┘
│                  │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌──────▼──────────────┐
│  Manager    │  │  Research Agent  │  │   Analysis Agent    │
│  Agent      │  │  (per competitor)│  │   RAG + SWOT +      │
│ Orchestrator│  │  Serper + Firecr │  │   Signal Scoring    │
└─────────────┘  └────────┬────────┘  └──────┬──────────────┘
│                  │
┌────────▼────────┐  ┌──────▼──────────────┐
│  Ingestion      │  │  Synthesizer Agent  │
│  Pipeline       │  │  Final Report       │
│  Chunk+Embed    │  │  Generation         │
└────────┬────────┘  └──────┬──────────────┘
│                  │
┌────────▼────────┐  ┌──────▼──────────────┐
│  Qdrant Vector  │  │  PDF Report         │
│  Database       │  │  (ReportLab)        │
│  (Cloud)        │  │                     │
└─────────────────┘  └─────────────────────┘

---

## Agent Roles

| Agent | Role | Tools |
|---|---|---|
| **Manager Agent** | Chief Intelligence Officer — orchestrates the crew | CrewAI hierarchical process, task delegation |
| **Research Agent** | Market Intelligence Collector — one per competitor | Serper API, Firecrawl, rate-limited retries |
| **Analysis Agent** | Strategy Analyst — SWOT + signal scoring | RAG (Qdrant), Mistral AI, SWOT framework |
| **Synthesizer Agent** | Executive Report Writer — unified report | Multi-company synthesis, recommendation engine |
| **Quality Guard** | Validation — error recovery + fallback | Pydantic validation, retry logic (3 attempts) |

---

## Tech Stack

### Backend
- **Python 3.10** — core language
- **CrewAI** — multi-agent orchestration framework
- **LangChain + Mistral AI** — LLM reasoning and RAG pipelines
- **Qdrant Cloud** — vector database for semantic search
- **FastAPI + Uvicorn** — REST API server
- **Sentence Transformers** — local embeddings (all-MiniLM-L6-v2)
- **ReportLab** — PDF report generation
- **Serper API** — Google News search
- **Firecrawl** — web scraping

### Frontend
- **React 18 + Vite** — fast modern frontend
- **TailwindCSS** — utility-first styling
- **Chart.js + react-chartjs-2** — signal velocity charts
- **D3.js** — force-directed signal graph
- **Lucide React** — icons
- **date-fns** — date formatting

---

## Project Structure
Multi-Agent Competitive Intelligence System/
├── agents/
│   ├── analysis_agent.py      # RAG + SWOT + signal analysis
│   ├── manager_agent.py       # CrewAI orchestrator
│   ├── research_agent.py      # News scraping per competitor
│   └── synthesizer_agent.py   # Final report generation
├── config/
│   ├── competitors.yaml       # Define which companies to track
│   └── settings.py            # Central config loader
├── crew/
│   └── intelligence_crew.py   # CrewAI crew assembly
├── frontend/
│   ├── src/
│   │   ├── pages/             # Dashboard, Pipeline, Intelligence...
│   │   ├── components/        # Sidebar, TopBar, ConnectionStatus
│   │   └── services/api.js    # All API calls
│   └── dist/                  # Built frontend (served by FastAPI)
├── monitoring/
│   ├── logger.py              # Rich console + JSON file logging
│   └── run_tracker.py         # Per-run stats and history
├── pipelines/
│   ├── chunker.py             # Semantic text chunking
│   ├── ingestion_pipeline.py  # Full scrape→embed→upsert pipeline
│   └── signal_detector.py     # Weak signal detection + scoring
├── reports/
│   └── pdf_renderer.py        # ReportLab PDF generation
├── storage/
│   ├── database.py            # Local JSON article store
│   └── vector_store.py        # Qdrant client wrapper
├── tasks/
│   ├── analysis_task.py       # CrewAI task definitions
│   ├── research_task.py
│   └── synthesis_task.py
├── tools/
│   ├── rag_tool.py            # RAG retrieval from Qdrant
│   ├── scraper_tool.py        # Firecrawl scraping
│   ├── search_tool.py         # Serper news search
│   └── signal_scorer.py       # Velocity + sentiment scoring
├── api_server.py              # FastAPI server + pipeline trigger
├── main.py                    # Entry point
├── start.bat                  # One-click startup script
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md                  # This file

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Subrahmanyeswar/multi-agent-competitive-intelligence.git
cd multi-agent-competitive-intelligence
```

### 2. Set up Python environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

| Key | Where to get it | Free tier |
|---|---|---|
| `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/) | Yes |
| `SERPER_API_KEY` | [serper.dev](https://serper.dev/) | 2500 searches/month |
| `FIRECRAWL_API_KEY` | [firecrawl.dev](https://firecrawl.dev/) | 500 pages/month |
| `QDRANT_URL` + `QDRANT_API_KEY` | [cloud.qdrant.io](https://cloud.qdrant.io/) | 1GB free |

### 4. Configure competitors

Edit `config/competitors.yaml` to track the companies you want:
```yaml
competitors:
  - name: "OpenAI"
    domain: "openai.com"
    keywords: ["OpenAI", "ChatGPT", "GPT-4o"]
    categories: ["product", "partnership", "funding"]
```

### 5. Build and run
```bash
# Windows — double-click or run:
.\start.bat

# Manual start:
cd frontend && npm install && npm run build && cd ..
python main.py
```

Open **http://localhost:8000** in your browser.

### 6. Generate your first report

Click **Run Pipeline** in the dashboard. The system will:
1. Scrape latest news for all competitors
2. Chunk and embed articles into Qdrant
3. Run SWOT + signal analysis via Mistral AI
4. Generate a PDF competitive intelligence report

Full run takes approximately **5–10 minutes** on free API tiers.

---

## Report Output

Each pipeline run produces:
- **PDF report** with executive summary, SWOT analysis, key developments, weak signals, strategic recommendations, and 30-day outlook
- **JSON analyses** stored in `storage/analyses.json`
- **Run history** logged in `storage/run_history.json`

---

## Configuration

### Adding new competitors

Edit `config/competitors.yaml`:
```yaml
competitors:
  - name: "Anthropic"
    domain: "anthropic.com"
    keywords: ["Anthropic", "Claude", "Constitutional AI"]
    categories: ["product", "research", "funding"]
```

### Changing the LLM model

In `.env`:
MISTRAL_MODEL=mistral-large-latest   # More accurate, slower
MISTRAL_MODEL=mistral-small-latest   # Faster, good for free tier

### Scheduling weekly runs
```bash
python main.py --schedule
```
Runs every Monday at 08:00 automatically.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/run` | Trigger pipeline run |
| `GET` | `/api/status` | Current pipeline status |
| `GET` | `/api/competitors` | All tracked competitors + stats |
| `GET` | `/api/articles` | Collected articles (filter by company) |
| `GET` | `/api/signals` | Weak signal detection results |
| `GET` | `/api/analyses` | Latest SWOT analyses |
| `GET` | `/api/report/latest` | Latest report metadata |
| `GET` | `/api/report/download` | Download latest PDF report |
| `GET` | `/api/vector-stats` | Qdrant vector DB statistics |
| `GET` | `/api/runs` | Full run history |

Full API docs available at **http://localhost:8000/docs**

---

## Important Notes

- **Free tier safe** — designed to work within free API limits
- **Rate limiting handled** — automatic retry with exponential backoff
- **No data committed** — `.env` and `storage/` are gitignored
- **Lazy loading** — heavy AI libraries load only when pipeline runs

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Subrahmanyeswar Kolluru**

- **HuggingFace:** [huggingface.co/Subrahmanyeswar](https://huggingface.co/Subrahmanyeswar)
- **LinkedIn:** [linkedin.com/in/subrahmanyeswar-kolluru-914694293](https://www.linkedin.com/in/subrahmanyeswar-kolluru-914694293)

Built with CrewAI, LangChain, Mistral AI, Qdrant, React, and D3.js.

---
