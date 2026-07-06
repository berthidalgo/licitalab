"""
Supabase Loader - Carga de datos procesados a Supabase.
Diseñado para ser robusto y manejable para grandes volúmenes.
"""

import logging
from typing import List, Dict, Any
import polars as pl

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class SupabaseLoader:
    def __init__(self, table_name: str = "licitaciones"):
        self.client = get_supabase_client()
        self.table_name = table_name

    def insert_dataframe(self, df: pl.DataFrame, batch_size: int = 500) -> Dict[str, Any]:
        """
        Inserta un DataFrame de Polars en Supabase en lotes.
        """
        records = df.to_dicts()
        total = len(records)
        inserted = 0
        errors = 0

        logger.info(f"Insertando {total} registros en tabla '{self.table_name}'...")

        for i in range(0, total, batch_size):
            batch = records[i : i + batch_size]
            try:
                response = self.client.table(self.table_name).upsert(batch, on_conflict="ocid").execute()
                inserted += len(batch)
                logger.info(f"  Lote {i//batch_size + 1}: {len(batch)} registros insertados/actualizados")
            except Exception as e:
                errors += len(batch)
                logger.error(f"Error insertando lote: {e}")

        result = {
            "total": total,
            "inserted": inserted,
            "errors": errors,
            "table": self.table_name,
        }

        logger.info(f"✅ Carga completada: {result}")
        return result

    def insert_records(self, records: List[Dict[str, Any]], batch_size: int = 500) -> Dict[str, Any]:
        """Versión para lista de diccionarios."""
        df = pl.DataFrame(records)
        return self.insert_dataframe(df, batch_size=batch_size)
