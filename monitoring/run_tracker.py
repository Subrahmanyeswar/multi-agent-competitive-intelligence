import json
import logging
from pathlib import Path
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)
RUN_LOG_PATH = Path(__file__).parent.parent / "storage" / "run_history.json"

class RunTracker:
    """
    Tracks each pipeline run — start time, end time, stats, errors.
    Persists to storage/run_history.json for audit and debugging.
    """
    
    def __init__(self):
        self.current_run = {}
    
    def start_run(self, run_type: str = "weekly") -> str:
        run_id = datetime.utcnow().strftime("run_%Y%m%d_%H%M%S")
        self.current_run = {
            "run_id": run_id,
            "run_type": run_type,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "running",
            "stages": {},
            "errors": [],
            "report_path": None,
        }
        logger.info(f"[RunTracker] Started run: {run_id}")
        return run_id
    
    def log_stage(self, stage_name: str, status: str, details: dict = None):
        self.current_run["stages"][stage_name] = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }
        logger.info(f"[RunTracker] Stage '{stage_name}': {status}")
    
    def log_error(self, stage: str, error: str):
        self.current_run["errors"].append({
            "stage": stage,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        })
        logger.error(f"[RunTracker] Error in '{stage}': {error}")
    
    def complete_run(self, status: str = "success", report_path: str = None):
        self.current_run["completed_at"] = datetime.utcnow().isoformat()
        self.current_run["status"] = status
        self.current_run["report_path"] = report_path
        self._save()
        logger.info(f"[RunTracker] Run completed: {status}")
        return self.current_run
    
    def _save(self):
        history = self._load_history()
        history.append(self.current_run)
        RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RUN_LOG_PATH, "w") as f:
            json.dump(history, f, indent=2)
    
    def _load_history(self) -> list:
        if not RUN_LOG_PATH.exists():
            return []
        with open(RUN_LOG_PATH) as f:
            return json.load(f)
    
    def get_last_run(self) -> dict:
        history = self._load_history()
        return history[-1] if history else {}
    
    def print_run_summary(self, run: dict):
        from rich.table import Table
        from rich.console import Console
        c = Console()
        
        c.print(f"\n[bold blue]Run Summary: {run.get('run_id', 'N/A')}[/bold blue]")
        c.print(f"Status: [{'green' if run['status'] == 'success' else 'red'}]{run['status']}[/]")
        c.print(f"Started:   {run.get('started_at', 'N/A')}")
        c.print(f"Completed: {run.get('completed_at', 'N/A')}")
        
        if run.get("report_path"):
            c.print(f"Report: [green]{run['report_path']}[/green]")
        
        if run.get("errors"):
            c.print(f"\n[red]Errors ({len(run['errors'])}):[/red]")
            for err in run["errors"]:
                c.print(f"  [{err['stage']}] {err['error']}")
        
        c.print("")
