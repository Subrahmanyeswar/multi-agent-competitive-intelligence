import warnings
warnings.filterwarnings("ignore")
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import asyncio
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Any, cast, List, Dict
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Competitive Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
REPORTS_DIR = BASE_DIR / "reports"
RUN_HISTORY = STORAGE_DIR / "run_history.json"
ARTICLES_DB = STORAGE_DIR / "articles.json"

pipeline_status = {
    "running": False, 
    "stage": "idle", 
    "message": "Ready. Click Run Pipeline to start.", 
    "started_at": None
}

def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

@app.get("/api/status")
def get_status():
    return pipeline_status

@app.get("/api/runs")
def get_runs():
    history = load_json(RUN_HISTORY, [])
    return {"runs": history[-20:], "total": len(history)}

@app.get("/api/competitors")
def get_competitors():
    from config.settings import settings
    competitors = settings.load_competitors()
    articles = load_json(ARTICLES_DB, [])
    result = []
    for c in competitors:
        name = c["name"]
        company_articles = [a for a in articles if a.get("company") == name]
        result.append({
            **c,
            "article_count": len(company_articles),
            "last_article": company_articles[-1].get("date", "") if company_articles else "",
        })
    return {"competitors": result}

@app.get("/api/articles")
def get_articles(company: str = "", limit: int = 50):
    raw_articles = load_json(ARTICLES_DB, [])
    if company:
        raw_articles = [a for a in raw_articles if isinstance(a, dict) and a.get("company") == company]
    
    # Sort and cast to Any to satisfy strict static analyzers that struggle with Sequence vs List slicing
    sorted_data = sorted(raw_articles, key=lambda x: x.get("stored_at", "") if isinstance(x, dict) else "", reverse=True)
    result_slice = cast(Any, sorted_data)[:limit]
    return {"articles": result_slice, "total": len(sorted_data)}

@app.get("/api/signals")
def get_signals():
    from config.settings import settings
    from pipelines.signal_detector import SignalDetector
    competitors = settings.load_competitors()
    names = [c["name"] for c in competitors]
    try:
        detector = SignalDetector()
        result = detector.run_full_detection(names)
        return result
    except Exception as e:
        return {"error": str(e), "topic_signals": [], "company_momentum": []}

@app.get("/api/analyses")
def get_analyses():
    history = load_json(RUN_HISTORY, [])
    analyses_store = BASE_DIR / "storage" / "analyses.json"
    analyses = load_json(analyses_store, [])
    return {"analyses": analyses}

@app.get("/api/report/latest")
def get_latest_report():
    reports = sorted(REPORTS_DIR.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not reports:
        return {"error": "No reports found"}
    latest = reports[0]
    size_mb = float(latest.stat().st_size) / 1024.0 / 1024.0
    return {
        "filename": latest.name,
        "path": str(latest),
        "size_kb": float(f"{latest.stat().st_size / 1024:.1f}"),
        "generated_at": datetime.fromtimestamp(latest.stat().st_mtime).isoformat(),
    }

@app.get("/api/report/download")
def download_report():
    reports = sorted(REPORTS_DIR.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not reports:
        return JSONResponse({"error": "No reports found"}, status_code=404)
    return FileResponse(str(reports[0]), media_type="application/pdf", filename=reports[0].name)

@app.get("/api/vector-stats")
def get_vector_stats():
    try:
        from qdrant_client import QdrantClient
        from config.settings import settings
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        info = client.get_collection(settings.COLLECTION_NAME)
        return {
            "vectors_count": info.vectors_count or 0,
            "points_count": info.points_count or 0,
            "collection": settings.COLLECTION_NAME,
            "status": "green",
        }
    except Exception as e:
        return {
            "error": str(e),
            "vectors_count": 0,
            "points_count": 0,
            "collection": "competitor_news",
            "status": "unavailable",
        }

def run_pipeline_task():
    global pipeline_status
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from config.settings import settings
        
        pipeline_status["stage"] = "config_validation"
        pipeline_status["message"] = "Validating configuration..."
        settings.validate()
        competitors = settings.load_competitors()

        pipeline_status["stage"] = "scraping"
        pipeline_status["message"] = f"Scraping news for {len(competitors)} competitors: {', '.join([c['name'] for c in competitors])}..."
        from pipelines.ingestion_pipeline import IngestionPipeline
        ingestion = IngestionPipeline()
        ingestion_stats = ingestion.run_all()

        pipeline_status["stage"] = "analysis"
        pipeline_status["message"] = "Running AI analysis (this takes 3-5 mins on free tier)..."
        from agents.analysis_agent import AnalysisAgent
        analyst = AnalysisAgent()
        analyses = analyst.analyze_all(competitors)
        
        analyses_path = STORAGE_DIR / "analyses.json"
        import json
        with open(analyses_path, "w") as f:
            json.dump(analyses, f, indent=2)

        pipeline_status["stage"] = "synthesis"
        pipeline_status["message"] = "Synthesizing final report..."
        from agents.synthesizer_agent import SynthesizerAgent
        from pipelines.signal_detector import SignalDetector
        synthesizer = SynthesizerAgent()
        report_data = synthesizer.synthesize(analyses)
        
        detector = SignalDetector()
        signal_report = detector.run_full_detection([c["name"] for c in competitors])
        report_data["weak_signals"] = [
            {
                "signal": s["topic"].replace("_", " ").title() + " activity accelerating",
                "company": ", ".join(s.get("companies_involved", [])[:2]),
                "velocity_score": s.get("velocity", 0),
                "recommended_action": f"Monitor {s['topic']} developments closely.",
            }
            for s in signal_report.get("topic_signals", [])[:5]
        ]

        pipeline_status["stage"] = "rendering"
        pipeline_status["message"] = "Generating PDF report..."
        from reports.pdf_renderer import PDFRenderer
        renderer = PDFRenderer()
        renderer.render(report_data, analyses=analyses)

        from monitoring.run_tracker import RunTracker
        tracker = RunTracker()
        tracker.start_run("manual_trigger")
        tracker.log_stage("ingestion", "success", ingestion_stats.get("totals", {}))
        tracker.log_stage("analysis", "success", {"companies_analyzed": len(analyses)})
        tracker.log_stage("synthesis", "success", {})
        tracker.log_stage("pdf_render", "success", {})
        tracker.complete_run("success")

        pipeline_status = {
            "running": False,
            "stage": "complete",
            "message": "Pipeline complete. Report ready to download.",
            "started_at": None
        }

    except Exception as e:
        pipeline_status = {
            "running": False,
            "stage": "error", 
            "message": f"Error: {str(e)}",
            "started_at": None
        }

@app.post("/api/run")
async def trigger_run(background_tasks: BackgroundTasks):
    global pipeline_status
    if pipeline_status["running"]:
        return {"error": "Pipeline already running", "status": "running"}
    pipeline_status = {
        "running": True,
        "stage": "starting", 
        "message": "Pipeline triggered from dashboard...",
        "started_at": datetime.utcnow().isoformat()
    }
    background_tasks.add_task(run_pipeline_task)
    return {"status": "started", "message": "Pipeline started successfully"}

FRONTEND_BUILD = BASE_DIR / "frontend" / "dist"

if FRONTEND_BUILD.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_BUILD / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        index = FRONTEND_BUILD / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return JSONResponse({"error": "Frontend not built"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")

    print("\n" + "="*50)
    print("Competitive Intelligence System is starting...")
    print("UI Access: http://localhost:8000")
    print("API Docs:  http://localhost:8000/docs")
    print("="*50 + "\n")
    
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=False)
