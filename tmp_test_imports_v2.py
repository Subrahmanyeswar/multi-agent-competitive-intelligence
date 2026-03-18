import time
import sys

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
    print(f"Trying to import {mod}...", flush=True)
    start = time.time()
    try:
        __import__(mod)
        print(f"DONE: {mod} took {time.time() - start:.4f}s", flush=True)
    except Exception as e:
        print(f"ERROR: {mod} failed: {e}", flush=True)

print("All imports tested.", flush=True)
