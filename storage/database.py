import json
import os
from pathlib import Path
from datetime import datetime
from config.settings import settings

DB_PATH = settings.BASE_DIR / "storage" / "articles.json"

def load_db() -> list[dict]:
    if not DB_PATH.exists():
        return []
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_article(article: dict) -> None:
    db = load_db()
    article["stored_at"] = datetime.utcnow().isoformat()
    db.append(article)
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def get_articles_by_company(company: str) -> list[dict]:
    return [a for a in load_db() if a.get("company") == company]

def article_exists(url: str) -> bool:
    return any(a.get("url") == url for a in load_db())
