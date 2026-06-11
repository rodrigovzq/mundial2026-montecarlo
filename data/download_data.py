"""Descarga del dataset historico de partidos internacionales (SPEC Section 3.1).

Fuente primaria: martj42/international-football-results (GitHub).
Fallback: archivo local si la descarga falla.
"""

import os
import time
import logging
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

CSV_URL = (
    "https://raw.githubusercontent.com/martj42/"
    "international_results/master/results.csv"
)
DEFAULT_OUTPUT = Path(__file__).parent / "matches.csv"
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def download_matches(output_path: str | Path = DEFAULT_OUTPUT) -> bool:
    """Descarga el dataset de partidos historicos.

    Args:
        output_path: Ruta donde guardar el CSV.

    Returns:
        True si la descarga fue exitosa o el archivo ya existe.
    """
    output = Path(output_path)

    if output.exists() and output.stat().st_size > 0:
        log.info("Archivo ya existe en %s -- saltando descarga", output)
        return True

    log.info("Descargando desde %s ...", CSV_URL)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(CSV_URL, timeout=30)
            response.raise_for_status()

            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, "wb") as f:
                f.write(response.content)

            log.info("Descargado %d bytes a %s", len(response.content), output)
            return True

        except requests.RequestException as e:
            log.warning("Intento %d/%d fallo: %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY ** attempt)

    log.error("No se pudo descargar despues de %d intentos", MAX_RETRIES)
    log.info("Verificando si existe archivo local como fallback...")
    return output.exists() and output.stat().st_size > 0


if __name__ == "__main__":
    success = download_matches()
    if success:
        log.info("Dataset listo para usar.")
    else:
        log.error("No se pudo obtener el dataset. Verifica conexion a internet.")
        exit(1)
