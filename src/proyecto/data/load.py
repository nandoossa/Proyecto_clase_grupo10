"""Carga de los datos originales de Saber 11 Antioquia.

El CSV no se sube a GitHub (está en `.gitignore`). La primera vez que se carga, se descarga
desde datos.gov.co y se guarda tal cual en `data/raw/`; las siguientes veces se lee la copia
local, para no descargar las 144.766 filas en cada ejecución.
"""
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

# Resultados Saber 11 (recurso kgxf-xxbe), periodo 20224, colegios de Antioquia.
SABER11_URL = (
    "https://www.datos.gov.co/resource/kgxf-xxbe.csv?"
    "$where=periodo=%2720224%27%20AND%20cole_depto_ubicacion=%27ANTIOQUIA%27"
    "&$order=estu_consecutivo&$limit=200000"
)
RAW_FILENAME = "saber11_antioquia_2022.csv"


def load_raw_saber11(raw_dir: Path | str, url: str = SABER11_URL) -> pd.DataFrame:
    """Devuelve los datos originales; los descarga a `raw_dir` si todavía no están.

    El archivo se guarda exactamente como lo entrega la fuente (sin modificarlo) y se
    escribe primero en un temporal, para que una descarga interrumpida no deje un CSV a medias.
    """
    raw_dir = Path(raw_dir)
    path = raw_dir / RAW_FILENAME
    if not path.exists():
        raw_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".csv.part")
        print(f"No existe {path.name}: descargando desde datos.gov.co (puede tardar unos minutos)...")
        urlretrieve(url, tmp_path)
        tmp_path.replace(path)
        print(f"Guardado en {path}")
    return pd.read_csv(path, low_memory=False)
