import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestImports")

modules = [
    "fastapi",
    "uvicorn",
    "qdrant_client",
    "config.settings",
    "storage.vector_store",
    "pipelines.chunker",
    "tools.signal_scorer",
    "pipelines.signal_detector",
    "pipelines.ingestion_pipeline",
    "agents.analysis_agent",
    "agents.synthesizer_agent",
    "agents.manager_agent",
]

for mod in modules:
    start = time.time()
    try:
        __import__(mod)
        logger.info(f"Imported {mod} in {time.time() - start:.4f}s")
    except Exception as e:
        logger.error(f"Failed to import {mod}: {e}")
