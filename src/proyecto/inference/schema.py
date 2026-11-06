"""Esquema de entrada del modelo: qué columnas espera, qué rangos son plausibles y qué categorías conoce.

El esquema es un archivo (`models/input_schema.json`) que viaja con el modelo. Lo usan `predict.py` (para validar
entradas) y la app (para construir su formulario).

Solo **regresión** (estimar `punt_global`). La rama de clasificación de la plantilla del curso (clases, matriz de costos,
umbral de revisión) se quitó al preparar el despliegue (revisión de la app, H3), como anunció la especificación de la
etapa 8.

Uso típico (notebook 08):

    from proyecto.inference.schema import build_schema
    schema = build_schema(train, numeric=[...], categorical=[...], valid_range={"edad": (13, 80)},
                          warn_only_categories=["cole_cod_mcpio_ubicacion", "estu_cod_reside_mcpio"],
                          path=ROOT / "models" / "input_schema.json")

Todo lo que el esquema guarda (categorías, rangos, medianas, `nullable`) se calcula **solo con la tabla que recibe
`build_schema`**, que debe ser el ENTRENAMIENTO; nada se calcula en el momento de predecir.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _is_integer_column(values: pd.Series) -> bool:
    """True si todos los valores no vacíos son enteros."""
    clean = values.dropna()
    return bool(len(clean)) and bool((clean == np.round(clean)).all())


def build_schema(
    df: pd.DataFrame,
    numeric: list[str],
    categorical: list[str],
    valid_range: dict | None = None,
    labels: dict | None = None,
    path: str | Path | None = None,
    task: str = "regression",
    warn_only_categories: list[str] | None = None,
) -> dict:
    """Construye (y opcionalmente guarda) el esquema de entrada a partir de los datos de ENTRENAMIENTO.

    - `df`: datos de entrenamiento, con las columnas de entrada (sin la columna objetivo).
    - `numeric` / `categorical`: columnas que el modelo necesita, tal como llegan en una fila nueva.
    - `valid_range`: opcional; {columna: (mínimo, máximo)} de lo que es POSIBLE. Fuera de ese rango, `predict` se niega a
      responder. Distinto del rango observado, que solo genera una advertencia.
    - `labels`: opcional; {columna: etiqueta legible}.
    - `task`: solo se acepta "regression" (se conserva el parámetro porque el notebook 08 lo pasa).
    - `warn_only_categories`: categóricas en las que un valor no visto da advertencia y no error (por ejemplo, códigos de
      municipio que el modelo agrupa como «poco frecuente»).
    """
    if task != "regression":
        raise ValueError(f"Este proyecto solo admite task='regression'; llegó {task!r}")
    missing = [c for c in numeric + categorical if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en los datos: {', '.join(missing)}")

    schema = {
        "task": task,
        "numeric": list(numeric),
        "categorical": list(categorical),
        "categories": {c: sorted(df[c].dropna().astype(str).unique().tolist()) for c in categorical},
        "observed_range": {},
        "median": {},
        "integer_columns": [],
        "valid_range": {k: [float(v[0]), float(v[1])] for k, v in (valid_range or {}).items()},
        "labels": dict(labels or {}),
        # Columnas que tenían vacíos en el entrenamiento: aceptan «sin respuesta» (el modelo aprendió a usar la ausencia)
        "nullable": [c for c in numeric + categorical if df[c].isna().any()],
        "warn_only_categories": list(warn_only_categories or []),
    }
    for col in numeric:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        if values.empty:
            raise ValueError(f"La columna numérica '{col}' no tiene ningún valor numérico")
        schema["observed_range"][col] = [float(values.min()), float(values.max())]
        schema["median"][col] = float(values.median())   # de `df` (el entrenamiento); solo informativa
        if _is_integer_column(values):
            schema["integer_columns"].append(col)
    if path is not None:
        save_schema(schema, path)
    return schema


def save_schema(schema: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")


def load_schema(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
