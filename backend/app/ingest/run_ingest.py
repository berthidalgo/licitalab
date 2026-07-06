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
        help="URL directa del archivo releases JSONL. Si no se pasa, usa la del .env o pide una.",
        default=None,
    )
    args = parser.parse_args()

    settings = get_settings()

    # TODO: En el futuro moveremos esto a settings
    releases_url = args.url

    if not releases_url:
        print("⚠️  Debes proporcionar una URL de releases.")
        print("Ve a https://contratacionesabiertas.oece.gob.pe/descargas y copia el enlace de 'Releases' (JSON).")
        print("\nEjemplo de ejecución:")
        print('  python -m app.ingest.run_ingest --url "https://..."')
        sys.exit(1)

    pipeline = IngestionPipeline()
    result = pipeline.run(releases_url=releases_url)

    if result.get("status") == "success":
        print("\n🎉 Ingesta finalizada exitosamente")
        print(f"Registros procesados: {result.get('total_records')}")
        print(f"Archivo procesado: {result.get('processed_file')}")
    else:
        print("\n❌ Ingesta falló")
        print(result)
        sys.exit(1)


if __name__ == "__main__":
    main()
