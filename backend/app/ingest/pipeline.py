"""
Ingestion Pipeline - Orquestador principal para la ingesta de OCDS.
Staff-level: logging, métricas, manejo de errores, extensibilidad.
"""

import logging
from pathlib import Path
from datetime import datetime

from .downloader import OCECDownloader
from .processor import OCDSProcessor

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        raw_dir: Path = Path("data/raw"),
        processed_dir: Path = Path("data/processed"),
    ):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.downloader = OCECDownloader(output_dir=raw_dir)
        self.processor = OCDSProcessor()

    def run(
        self,
        releases_url: str,
        run_id: str | None = None,
    ) -> dict:
        """
        Ejecuta el pipeline completo de ingesta.

        Args:
            releases_url: URL directa al archivo releases (JSONL) del OECE.
            run_id: Identificador opcional de la ejecución.

        Returns:
            Diccionario con métricas de la ejecución.
        """
        if not run_id:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"🚀 Iniciando ingesta OCDS - run_id={run_id}")

        try:
            # 1. Descarga
            raw_file = self.downloader.download_releases(
                url=releases_url,
                filename=f"releases_{run_id}.jsonl",
                force=False,
            )

            # 2. Procesamiento
            output_parquet = self.processed_dir / f"licitaciones_{run_id}.parquet"
            df = self.processor.process_file(raw_file, output_parquet)

            metrics = {
                "run_id": run_id,
                "raw_file": str(raw_file),
                "processed_file": str(output_parquet),
                "total_records": len(df),
                "status": "success",
            }

            logger.info(f"✅ Ingesta completada exitosamente. Registros: {metrics['total_records']}")
            return metrics

        except Exception as e:
            logger.exception("❌ Error en el pipeline de ingesta")
            return {
                "run_id": run_id,
                "status": "error",
                "error": str(e),
            }
        finally:
            self.downloader.close()
