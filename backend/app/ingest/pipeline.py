"""
Ingestion Pipeline - Orquestador principal para la ingesta de OCDS.
Staff-level: logging, métricas, manejo de errores, extensibilidad.
"""

import logging
from pathlib import Path
from datetime import datetime

from .downloader import OCECDownloader
from .processor import OCDSProcessor
from .loader import SupabaseLoader

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
        releases_url: str | None = None,
        run_id: str | None = None,
        load_to_supabase: bool = False,
        supabase_table: str = "licitaciones",
        use_api: bool = True,
        api_limit: int = 20,
        api_page: int = 1,
        data_segmentation: str | None = None,
    ) -> dict:
        """
        Ejecuta el pipeline completo de ingesta.

        Args:
            releases_url: URL directa al archivo releases (JSONL) del OECE.
            run_id: Identificador opcional de la ejecución.
            load_to_supabase: Si es True, carga los datos a Supabase.
            supabase_table: Nombre de la tabla en Supabase.

        Returns:
            Diccionario con métricas de la ejecución.
        """
        if not run_id:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"🚀 Iniciando ingesta OCDS - run_id={run_id} (use_api={use_api})")

        try:
            if use_api:
                # Nueva vía recomendada: API v1 (mejor para incremental y free tier)
                logger.info("Usando API /api/v1/releases (paginado + filtros)")
                df = self._fetch_via_api(
                    limit=api_limit,
                    page=api_page,
                    data_segmentation=data_segmentation,
                    run_id=run_id,
                )
                output_parquet = self.processed_dir / f"licitaciones_{run_id}.parquet"
                df.write_parquet(output_parquet)
            else:
                # 1. Descarga bulk (legacy)
                if not releases_url:
                    raise ValueError("releases_url requerido cuando use_api=False")
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
                "loaded_to_supabase": False,
            }

            # 3. Carga opcional a Supabase
            if load_to_supabase:
                loader = SupabaseLoader(table_name=supabase_table)
                load_result = loader.insert_dataframe(df)
                metrics["loaded_to_supabase"] = True
                metrics["supabase_load_result"] = load_result
                logger.info("✅ Datos cargados a Supabase")

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
            if hasattr(self, 'downloader') and self.downloader:
                try:
                    self.downloader.close()
                except:
                    pass

    def _fetch_via_api(
        self,
        limit: int = 20,
        page: int = 1,
        data_segmentation: str | None = None,
        run_id: str | None = None,
    ) -> "pl.DataFrame":
        """
        Ingesta vía API oficial /api/v1/releases (recomendado).
        Retorna DataFrame compatible con el processor.
        """
        import httpx
        import polars as pl

        base = "https://contratacionesabiertas.oece.gob.pe/api/v1/releases"
        params = {"limit": limit, "page": page}
        if data_segmentation:
            params["dataSegmentation"] = data_segmentation

        logger.info(f"Fetching from API: {base} params={params}")

        with httpx.Client(timeout=60, follow_redirects=True) as client:
            resp = client.get(base, params=params)
            resp.raise_for_status()
            data = resp.json()

        releases = data.get("releases", [])
        logger.info(f"API devolvió {len(releases)} releases")

        if not releases:
            return pl.DataFrame()

        # Convertimos a estructura similar a lo que espera el processor (raw OCDS style)
        # Para compatibilidad rápida, creamos un DF con columna 'releases' o procesamos directo.
        # Mejor: reutilizamos lógica similar al processor.
        # Por simplicidad aquí devolvemos un DF con las releases como lista de dicts y dejamos que el caller use el processor.extract si quiere.

        # Para integración inmediata: devolvemos un DF "plano" usando las mismas columnas que el processor.
        # Llamaremos al extract logic del processor.
        raw_df = pl.DataFrame({"releases": releases})  # truco para simular
        # El processor espera el JSONL cargado como DF con columnas anidadas.
        # Mejor enfoque: extraer directamente aquí.

        # Extraemos usando la misma lógica que el processor para ser consistente.
        processed = self.processor._extract_from_list(releases) if hasattr(self.processor, '_extract_from_list') else None

        if processed is None:
            # Fallback simple: usar el extract_licitaciones del processor
            # Creamos un DF dummy con la estructura que el processor.load_releases produce.
            # En la práctica, el processor.process_file hace load + extract.
            # Para API devolvemos el DF ya extraído listo para Supabase.

            # Llamamos directamente al extract (asumiendo que el processor lo expone o lo copiamos).
            # Para que funcione ya, implementamos un extract mínimo aquí y lo devolvemos.
            extracted = []
            for r in releases:
                t = r.get("tender", {}) or {}
                b = r.get("buyer", {}) or {}
                extracted.append({
                    "ocid": r.get("ocid"),
                    "id": r.get("id"),
                    "date": r.get("date"),
                    "tender_title": t.get("title"),
                    "tender_description": t.get("description"),
                    "tender_status": t.get("status"),
                    "tender_value_amount": (t.get("value") or {}).get("amount"),
                    "tender_value_currency": (t.get("value") or {}).get("currency"),
                    "buyer_name": b.get("name"),
                    "buyer_id": b.get("id"),
                    "procurement_method": t.get("procurementMethod"),
                    "procurement_method_details": t.get("procurementMethodDetails"),
                    "tender_period_start": (t.get("tenderPeriod") or {}).get("startDate"),
                    "tender_period_end": (t.get("tenderPeriod") or {}).get("endDate"),
                    "number_of_tenderers": t.get("numberOfTenderers"),
                })

            df = pl.DataFrame(extracted)
            return df

        return processed
