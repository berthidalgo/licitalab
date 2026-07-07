from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from app.core.config import get_settings
from app.ingest.pipeline import IngestionPipeline
from app.db.supabase_client import get_supabase_client

settings = get_settings()
logger = logging.getLogger("api")
supabase = get_supabase_client()

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
        # Con use_api=True no es obligatorio el URL legacy

        logger.info(f"🚀 Background ingestion started (API v1 mode)")
        pipeline = IngestionPipeline()
        result = pipeline.run(
            releases_url=releases_url,
            load_to_supabase=load_to_supabase,
            supabase_table=table,
            use_api=True,
            data_segmentation="2026-07",
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
        "endpoints": {
            "health": "/health",
            "ingest_run": "POST /ingest/run",
            "ingest_status": "/ingest/status",
            "table_status": "/db/table-status",
            "licitaciones": "/licitaciones",
        },
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
        "note": "1. Primero verifica con GET /db/table-status que la tabla exista. 2. Revisa /ingest/status. 3. En Render free las ingestas grandes pueden tardar o fallar por tamaño/tiempo.",
    }


@app.get("/ingest/status")
async def ingest_status():
    """Devuelve el estado de la última ingesta."""
    return last_ingest_status


# ==================== DB / TABLE HELPERS ====================

@app.get("/db/table-status")
async def table_status():
    """
    Verifica si la tabla 'licitaciones' existe y cuántos registros tiene.
    Útil para confirmar que la tabla fue creada antes de ingestar.
    """
    try:
        response = (
            supabase.table("licitaciones")
            .select("*", count="exact")
            .limit(1)
            .execute()
        )
        return {
            "table": "licitaciones",
            "exists": True,
            "record_count": response.count or 0,
            "message": "Tabla existe y es accesible",
        }
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg.lower() or "does not exist" in error_msg.lower():
            return {
                "table": "licitaciones",
                "exists": False,
                "record_count": 0,
                "message": "La tabla no existe. Ejecuta el SQL de backend/app/db/create_licitaciones_table.sql en el SQL Editor de Supabase.",
            }
        return {
            "table": "licitaciones",
            "exists": False,
            "error": error_msg,
        }


# ==================== LICITACIONES READ ENDPOINTS ====================

@app.get("/licitaciones", response_model=List[Dict[str, Any]])
async def get_licitaciones(
    limit: int = Query(50, le=200),
    status: Optional[str] = None,
    buyer: Optional[str] = None,
):
    """
    Lista licitaciones (datos ya cargados en Supabase).
    Soporta filtros básicos.
    """
    try:
        query = supabase.table("licitaciones").select("*").limit(limit)

        if status:
            query = query.eq("tender_status", status)
        if buyer:
            query = query.ilike("buyer_name", f"%{buyer}%")

        response = query.execute()
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando licitaciones: {str(e)}")


@app.get("/licitaciones/{ocid}")
async def get_licitacion(ocid: str):
    """Obtiene una licitación por su ocid."""
    try:
        response = supabase.table("licitaciones").select("*").eq("ocid", ocid).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        return response.data
    except Exception as e:
        if "JSON object requested" in str(e) or "no rows" in str(e).lower():
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        raise HTTPException(status_code=500, detail=str(e))
