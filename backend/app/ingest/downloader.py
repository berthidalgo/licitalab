"""
OCDS Downloader - Descarga robusta de datos del Portal de Contrataciones Abiertas (OECE).
Staff Engineer level: streaming, retries, progress, error handling.
"""

import httpx
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OCECDownloader:
    """
    Descargador robusto de archivos OCDS (principalmente releases en formato JSONL).
    Soporta descargas grandes con streaming y reintentos.
    """

    def __init__(
        self,
        output_dir: Path = Path("data/raw"),
        timeout: int = 300,
        max_retries: int = 3,
    ):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)

    def download_releases(
        self,
        url: str,
        filename: Optional[str] = None,
        force: bool = False,
    ) -> Path:
        """
        Descarga un archivo de releases OCDS (JSONL recomendado).

        Args:
            url: URL directa al archivo (ej: desde https://contratacionesabiertas.oece.gob.pe/descargas)
            filename: Nombre del archivo local. Si no se provee, se infiere del URL o timestamp.
            force: Sobrescribir si ya existe.

        Returns:
            Path al archivo descargado.
        """
        if not filename:
            # Intentar extraer nombre del URL o usar timestamp
            filename = url.split("/")[-1] or f"releases_{datetime.now().strftime('%Y%m%d')}.jsonl"

        output_path = self.output_dir / filename

        if output_path.exists() and not force:
            logger.info(f"Archivo ya existe: {output_path}. Usando cache. Usa force=True para descargar de nuevo.")
            return output_path

        logger.info(f"Descargando OCDS desde: {url}")

        for attempt in range(1, self.max_retries + 1):
            try:
                with self.client.stream("GET", url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get("content-length", 0))

                    with open(output_path, "wb") as f:
                        downloaded = 0
                        for chunk in response.iter_bytes(chunk_size=1024 * 1024):  # 1MB chunks
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0 and downloaded % (50 * 1024 * 1024) == 0:  # log cada ~50MB
                                progress = (downloaded / total_size) * 100
                                logger.info(f"Progreso: {progress:.1f}% ({downloaded / 1e6:.1f} MB)")

                logger.info(f"Descarga completada: {output_path} ({output_path.stat().st_size / 1e6:.1f} MB)")
                return output_path

            except Exception as e:
                logger.warning(f"Intento {attempt}/{self.max_retries} falló: {e}")
                if attempt == self.max_retries:
                    raise RuntimeError(f"No se pudo descargar después de {self.max_retries} intentos: {url}") from e

        return output_path

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
