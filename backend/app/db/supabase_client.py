"""
Supabase Client - Cliente oficial de Supabase para LicitAI Perú.
Staff Engineer level: singleton / cached client, manejo de errores, soporte para service role.
"""

from supabase import create_client, Client
from functools import lru_cache
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Devuelve un cliente de Supabase cacheado.
    Usa SUPABASE_URL y SUPABASE_KEY del .env
    """
    settings = get_settings()

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")

    client: Client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_KEY
    )

    logger.info("✅ Supabase client inicializado correctamente")
    return client


# Instancia global para uso rápido (recomendado usar get_supabase_client() en la mayoría de casos)
supabase: Client = get_supabase_client()
