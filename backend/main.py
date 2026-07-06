from fastapi import FastAPI
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="LicitAI Perú API",
    description="API inteligente de licitaciones públicas del Estado Peruano",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {
        "message": "LicitAI Perú API - Día 1 completado",
        "status": "healthy",
        "env": settings.ENV
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
