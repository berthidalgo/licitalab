"""
Script de entrada para ejecutar la ingesta de datos OCDS.

Uso:
    cd backend
    python -m app.ingest.run_ingest

O con URL específica:
    python -m app.ingest.run_ingest --url "https://..."

Obtén las URLs actualizadas desde:
    https://contratacionesabiertas.oece.gob.pe/descargas
"""

import argparse
import logging
import sys
from pathlib import Path

# Añadir el directorio padre al path para poder importar
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.ingest.pipeline import IngestionPipeline
from app.core.config import get_settings

# Configuración básica de logging (mejorar después con structlog o similar)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("ingest")


def main():
    parser = argparse.ArgumentParser(description="Ingesta robusta de datos OCDS del OECE")
    parser.add_argument(
        "--url",
        type=str,
        help="URL directa del archivo releases JSONL",
        default=None,
    )
    parser.add_argument(
        "--load-to-supabase",
        action="store_true",
        help="Carga automáticamente los datos a Supabase después de procesarlos",
    )
    parser.add_argument(
        "--table",
        type=str,
        default="licitaciones",
        help="Nombre de la tabla en Supabase (default: licitaciones)",
    )
    args = parser.parse_args()

    settings = get_settings()

    releases_url = args.url or getattr(settings, "OCDS_RELEASES_URL", None)

    if not releases_url:
        print("⚠️  Debes proporcionar una URL de releases.")
        print("Ve a https://contratacionesabiertas.oece.gob.pe/descargas y copia el enlace de 'Releases' (JSON).")
        print("\nEjemplo:")
        print('  python -m app.ingest.run_ingest --url "https://..." --load-to-supabase')
        sys.exit(1)

    pipeline = IngestionPipeline()
    result = pipeline.run(
        releases_url=releases_url,
        load_to_supabase=args.load_to_supabase,
        supabase_table=args.table,
    )

    if result.get("status") == "success":
        print("\n🎉 Ingesta finalizada exitosamente")
        print(f"Registros procesados: {result.get('total_records')}")
        print(f"Archivo procesado: {result.get('processed_file')}")
        if result.get("loaded_to_supabase"):
            print(f"Datos cargados a Supabase tabla: {args.table}")
    else:
        print("\n❌ Ingesta falló")
        print(result)
        sys.exit(1)


if __name__ == "__main__":
    main()
