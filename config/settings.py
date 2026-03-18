import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

class Settings:
    # API Keys
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "competitor_news")
    
    # Models
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    
    # RAG
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "8"))
    
    # Output
    REPORT_OUTPUT_DIR: Path = BASE_DIR / os.getenv("REPORT_OUTPUT_DIR", "reports")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Base directory reference
    BASE_DIR: Path = BASE_DIR
    
    @classmethod
    def load_competitors(cls) -> list[dict]:
        config_path = BASE_DIR / "config" / "competitors.yaml"
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("competitors", [])
    
    @classmethod
    def validate(cls) -> None:
        required = ["MISTRAL_API_KEY", "SERPER_API_KEY", "FIRECRAWL_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
        missing = [k for k in required if not getattr(cls, k)]
        if missing:
            raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")

settings = Settings()
