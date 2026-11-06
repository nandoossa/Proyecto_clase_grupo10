"""Esquema de entrada del modelo: qué columnas espera, qué rangos son plausibles y qué categorías conoce.

El esquema es un archivo (`models/input_schema.json`) que viaja con el modelo. Lo usan
`predict.py` (para validar entradas) y la app (para construir su formulario).

Uso típico, en el notebook de inferencia:

    from proyecto.inference.schema import build_schema
    schema = build_schema(train, numeric=[...], categorical=[...], class_names=["no", "si"],
                          cost_matrix=None, valid_range={"edad": (0, 120)}, path="../models/input_schema.json")

Sirve para **clasificación** (plantilla del curso) y, desde la etapa 8, para **regresión** (`task="regression"`, el caso
de este proyecto: estimar `punt_global`). En regresión el esquema no lleva clases ni matriz de costos, y además dice qué
columnas admiten vacío (`nullable`) y en qué categóricas un valor nuevo solo genera advertencia (`warn_only_categories`).

Todo lo que el esquema guarda (categorías, rangos, medianas) se calcula **solo con la tabla que recibe `build_schema`**,
que debe ser el ENTRENAMIENTO; nada se calcula en el momento de predecir.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _is_integer_column(values: pd.Series) -> bool:
    """True si todos los valores no vacíos son enteros (se usará un campo entero en la app)."""
    clean = values.dropna()
    return bool(len(clean)) and bool((clean == np.round(clean)).all())


def build_schema(
    df: pd.DataFrame,
    numeric: list[str],
    categorical: list[str],
    class_names: list[str] | None = None,
    cost_matrix=None,
    valid_range: dict | None = None,
    labels: dict | None = None,
    review_threshold: float = 0.55,
    path: str | Path | None = None,
    task: str = "classification",
    warn_only_categories: list[str] | None = None,
) -> dict:
    """Construye (y opcionalmente guarda) el esquema de entrada a partir de los datos de ENTRENAMIENTO.

    - `df`: datos de entrenamiento, con las columnas de entrada (sin la columna objetivo).
    - `numeric` / `categorical`: columnas que el modelo necesita, tal como llegan en una fila nueva.
    - `class_names`: nombres de las clases, en el orden de las columnas de `predict_proba`.
    - `cost_matrix`: opcional; matriz k x k (filas = clase real, columnas = clase decidida). Si se da, la
      decisión será la de menor costo esperado; si no, la clase más probable.
    - `valid_range`: opcional; {columna: (mínimo, máximo)} de lo que es POSIBLE en el mundo real. Fuera de ese
      rango, `predict` se niega a responder. Distinto del rango observado, que solo genera una advertencia.
    - `labels`: opcional; {columna: etiqueta legible} para la app.
    - `task`: "classification" (plantilla) o "regression" (sin clases ni costos; agrega `nullable`).
    - `warn_only_categories`: solo en regresión; categóricas en las que un valor no visto da advertencia y no error
      (por ejemplo, códigos de municipio que el modelo agrupa como «poco frecuente»).
    """
    if task not in ("classification", "regression"):
        raise ValueError(f"task debe ser 'classification' o 'regression'; llegó {task!r}")
    missing = [c for c in numeric + categorical if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en los datos: {', '.join(missing)}")
    if task == "classification" and (class_names is None or len(class_names) < 2):
        raise ValueError("class_names debe tener al menos 2 clases")
    if cost_matrix is not None:
        cost = np.asarray(cost_matrix, dtype=float)
        if cost.shape != (len(class_names), len(class_names)):
            raise ValueError(f"cost_matrix debe ser {len(class_names)} x {len(class_names)}; llegó {cost.shape}")

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
    }
    if task == "classification":
        schema["class_names"] = [str(c) for c in class_names]
        schema["review_threshold"] = float(review_threshold)
    else:
        # Columnas que tenían vacíos en el entrenamiento: aceptan «sin respuesta» (el modelo aprendió a usar la ausencia)
        schema["nullable"] = [c for c in numeric + categorical if df[c].isna().any()]
        schema["warn_only_categories"] = list(warn_only_categories or [])
    for col in numeric:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        if values.empty:
            raise ValueError(f"La columna numérica '{col}' no tiene ningún valor numérico")
        schema["observed_range"][col] = [float(values.min()), float(values.max())]
        schema["median"][col] = float(values.median())   # de `df` (el entrenamiento); solo informativa para la app
        if _is_integer_column(values):
            schema["integer_columns"].append(col)
    if cost_matrix is not None:
        schema["cost_matrix"] = np.asarray(cost_matrix, dtype=float).tolist()
    if path is not None:
        save_schema(schema, path)
    return schema


def save_schema(schema: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")


def load_schema(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
