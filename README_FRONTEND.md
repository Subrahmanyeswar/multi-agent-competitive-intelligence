# Competitive Intelligence Dashboard

## Quick Start (Production)
Double-click start.bat

Open: http://localhost:8000

## Quick Start (Development)
Terminal 1:
  venv\Scripts\activate
  python api_server.py

Terminal 2:
  cd frontend
  npm run dev

Open: http://localhost:5173

## Pages
- Dashboard     — Live stats, competitor overview, run history
- Live Pipeline — Animated multi-agent pipeline visualizer
- Agent Activity — All 5 agents with roles, tools, and status
- Intelligence  — SWOT analysis, signal charts, key developments
- Signal Graph  — D3 force-directed network of topics and companies
- Reports       — PDF download, inline report preview, run history
- Data Store    — All collected articles, vector DB stats, search

## Tech Stack
Backend: FastAPI + CrewAI + Mistral AI + Qdrant
Frontend: React + Vite + TailwindCSS + Chart.js + D3.js
