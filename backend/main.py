from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.config import get_settings
from app.ingest.pipeline import IngestionPipeline

settings = get_settings()
logger = logging.getLogger("api")

app = FastAPI(
    title="LicitAI Perú API",
    description="API inteligente de licitaciones públicas del Estado Peruano",
    version="0.1.0"
)

# Simple in-memory status for last ingestion run
last_ingest_status: dict = {
    "status": "never_run",
    "last_run": None,
    "records": 0,
    "error": None,
}


class IngestRequest(BaseModel):
    url: Optional[str] = None
    load_to_supabase: bool = True
    table: str = "licitaciones"


def _run_ingestion_background(url: Optional[str], load_to_supabase: bool, table: str):
    """Función que corre en background."""
    global last_ingest_status
    try:
        releases_url = url or settings.OCDS_RELEASES_URL
        if not releases_url:
            last_ingest_status = {
                "status": "error",
                "error": "No URL provided and OCDS_RELEASES_URL not configured",
            }
            return

        logger.info(f"🚀 Background ingestion started with url={releases_url}")
        pipeline = IngestionPipeline()
        result = pipeline.run(
            releases_url=releases_url,
            load_to_supabase=load_to_supabase,
            supabase_table=table,
        )

        if result.get("status") == "success":
            last_ingest_status = {
                "status": "success",
                "last_run": result.get("run_id"),
                "records": result.get("total_records", 0),
                "loaded_to_supabase": result.get("loaded_to_supabase", False),
                "error": None,
            }
            logger.info("✅ Background ingestion completed successfully")
        else:
            last_ingest_status = {
                "status": "error",
                "error": result.get("error"),
            }
    except Exception as e:
        logger.exception("Ingestion background failed")
        last_ingest_status = {"status": "error", "error": str(e)}


@app.get("/")
async def root():
    return {
        "message": "LicitAI Perú API",
        "status": "healthy",
        "env": settings.ENV,
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/ingest/run")
async def trigger_ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Dispara la ingesta de licitaciones desde OCDS.
    Corre en background para no bloquear la respuesta.
    """
    global last_ingest_status
    last_ingest_status["status"] = "started"

    background_tasks.add_task(
        _run_ingestion_background,
        request.url,
        request.load_to_supabase,
        request.table,
    )

    return {
        "message": "Ingesta iniciada en background",
        "status": "started",
        "note": "Revisa /ingest/status para el resultado. Nota: En Render free la ingesta grande puede tardar.",
    }


@app.get("/ingest/status")
async def ingest_status():
    """Devuelve el estado de la última ingesta."""
    return last_ingest_status
