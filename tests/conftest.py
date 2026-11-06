"""Configuración común de las pruebas.

- Permite ejecutar `pytest tests` desde la raíz del repo sin instalar el paquete.
- `school_frame`: tabla inventada con las columnas que entrega la etapa 3, compartida por test_models, test_tuning y
  test_evaluation (H7 de la auditoría de la etapa 7: antes se importaba de test_models.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402  (después de agregar src/ al path)
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from proyecto.data.split import GROUP_COL  # noqa: E402
from proyecto.models.train import TARGET  # noqa: E402


def _school_frame(n_schools: int = 40, per_school: int = 5) -> pd.DataFrame:
    """Tabla con las columnas que entrega la etapa 3; el puntaje depende del estrato y de la edad."""
    rng = np.random.default_rng(0)
    n = n_schools * per_school
    stratum = rng.integers(1, 7, n).astype(float)
    age = rng.integers(15, 20, n).astype(float)
    return pd.DataFrame({
        "edad": age,
        "fami_estratovivienda": stratum,
        "sin_estrato": np.zeros(n, dtype=int),
        "fami_personashogar": rng.integers(1, 6, n).astype(float),
        "fami_cuartoshogar": rng.integers(1, 7, n).astype(float),
        "cole_area_ubicacion": rng.choice(["URBANO", "RURAL"], n),
        "cole_bilingue": rng.choice(["N", "S"], n),
        "cole_caracter": rng.choice(["ACADÉMICO", "TÉCNICO"], n),
        "cole_genero": rng.choice(["MIXTO", "FEMENINO"], n),
        "cole_jornada": rng.choice(["MAÑANA", "TARDE", "UNICA"], n),
        "cole_naturaleza": rng.choice(["OFICIAL", "NO OFICIAL"], n),
        "cole_sede_principal": rng.choice(["S", "N"], n),
        "estu_genero": rng.choice(["F", "M"], n),
        "fami_educacionmadre": rng.choice(["Primaria completa", "Postgrado", "No sabe"], n),
        "fami_educacionpadre": rng.choice(["Ninguno", "Secundaria (Bachillerato) completa", "No Aplica"], n),
        "fami_tieneautomovil": rng.choice(["Si", "No"], n),
        "fami_tienecomputador": rng.choice(["Si", "No"], n),
        "fami_tieneinternet": rng.choice(["Si", "No"], n),
        "fami_tienelavadora": rng.choice(["Si", "No"], n),
        "cole_cod_mcpio_ubicacion": rng.choice([5001, 5088, 5360], n),
        "estu_cod_reside_mcpio": rng.choice([5001, 5088, 5360], n),
        GROUP_COL: np.repeat(np.arange(n_schools) + 1000, per_school),
        TARGET: 200 + 10 * stratum - 2 * age + rng.normal(0, 5, n),
    })


@pytest.fixture
def school_frame():
    """Fábrica de tablas inventadas: `school_frame(n_schools=40, per_school=5)`."""
    return _school_frame
