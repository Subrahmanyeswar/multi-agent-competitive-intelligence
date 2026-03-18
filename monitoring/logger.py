import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from config.settings import settings

BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

console = Console()

def setup_logging() -> logging.Logger:
    """
    Sets up dual logging:
    - Rich console handler (colored, readable for development)
    - JSON file handler (structured, for audit and debugging)
    """
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    
    # Rich console handler
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True,
        show_path=False,
    )
    rich_handler.setLevel(level)
    root.addHandler(rich_handler)
    
    # JSON file handler
    log_file = LOG_DIR / f"run_{datetime.utcnow().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root.addHandler(file_handler)
    
    return logging.getLogger("intel_system")


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)
