"""
OCDS Processor - Transformación robusta de datos OCDS usando Polars.
Enfocado en alto rendimiento para grandes volúmenes de licitaciones.
"""

import polars as pl
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OCDSProcessor:
    """
    Procesa archivos OCDS (JSONL) y los transforma en tablas estructuradas.
    Extrae campos clave para scoring y RAG.
    """

    def __init__(self):
        self.schema = {
            # Campos principales que nos interesan para el MVP
            "ocid": pl.Utf8,
            "id": pl.Utf8,
            "date": pl.Utf8,
            "tender_title": pl.Utf8,
            "tender_description": pl.Utf8,
            "tender_status": pl.Utf8,
            "tender_value_amount": pl.Float64,
            "tender_value_currency": pl.Utf8,
            "buyer_name": pl.Utf8,
            "buyer_id": pl.Utf8,
            "procurement_method": pl.Utf8,
            "procurement_method_details": pl.Utf8,
            "tender_period_start": pl.Utf8,
            "tender_period_end": pl.Utf8,
            "number_of_tenderers": pl.Int64,
        }

    def load_releases(self, file_path: Path) -> pl.DataFrame:
        """
        Carga un archivo releases JSONL de forma eficiente con Polars.
        """
        logger.info(f"Cargando releases desde {file_path}...")

        # Polars es excelente con NDJSON (JSONL)
        df = pl.read_ndjson(
            file_path,
            infer_schema_length=10000,  # más preciso para OCDS
            ignore_errors=True,
        )

        logger.info(f"Releases crudos cargados: {len(df)} filas")
        return df

    def extract_licitaciones(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Extrae y aplana los campos más importantes de cada release.
        Retorna un DataFrame limpio listo para guardar o cargar en DB.
        """
        logger.info("Extrayendo campos clave de licitaciones...")

        # OCDS tiene estructura anidada: tender, buyer, etc.
        # Usamos expresión para extraer de forma segura.

        processed = (
            df.with_columns([
                # Tender
                pl.col("tender").struct.field("title").alias("tender_title"),
                pl.col("tender").struct.field("description").alias("tender_description"),
                pl.col("tender").struct.field("status").alias("tender_status"),
                pl.col("tender").struct.field("value").struct.field("amount").alias("tender_value_amount"),
                pl.col("tender").struct.field("value").struct.field("currency").alias("tender_value_currency"),
                pl.col("tender").struct.field("procurementMethod").alias("procurement_method"),
                pl.col("tender").struct.field("procurementMethodDetails").alias("procurement_method_details"),

                # Períodos
                pl.col("tender").struct.field("tenderPeriod").struct.field("startDate").alias("tender_period_start"),
                pl.col("tender").struct.field("tenderPeriod").struct.field("endDate").alias("tender_period_end"),

                # Buyer (entidad compradora)
                pl.col("buyer").struct.field("name").alias("buyer_name"),
                pl.col("buyer").struct.field("id").alias("buyer_id"),

                # Número de oferentes (si existe)
                pl.col("tender").struct.field("numberOfTenderers").alias("number_of_tenderers"),
            ])
            .select([
                "ocid",
                "id",
                "date",
                "tender_title",
                "tender_description",
                "tender_status",
                "tender_value_amount",
                "tender_value_currency",
                "buyer_name",
                "buyer_id",
                "procurement_method",
                "procurement_method_details",
                "tender_period_start",
                "tender_period_end",
                "number_of_tenderers",
            ])
            .filter(pl.col("ocid").is_not_null())
        )

        # Limpieza básica
        processed = processed.with_columns([
            pl.col("tender_value_amount").fill_null(0.0),
            pl.col("tender_title").fill_null(""),
        ])

        logger.info(f"Licitaciones procesadas: {len(processed)} registros")
        return processed

    def save_parquet(self, df: pl.DataFrame, output_path: Path) -> None:
        """Guarda el DataFrame procesado en formato Parquet (muy eficiente)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(output_path)
        logger.info(f"Guardado en Parquet: {output_path} ({len(df)} filas)")

    def process_file(self, input_file: Path, output_parquet: Path) -> pl.DataFrame:
        """Pipeline completo: load + extract + save."""
        raw_df = self.load_releases(input_file)
        processed_df = self.extract_licitaciones(raw_df)
        self.save_parquet(processed_df, output_parquet)
        return processed_df
