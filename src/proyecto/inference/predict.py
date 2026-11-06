"""Inferencia: validar entradas y predecir (clasificación de la plantilla y regresión del proyecto).

**Regresión (este proyecto, etapa 8):** `predict_score(df, model, schema)` devuelve `puntaje_estimado`, sin redondear ni
recortar. Con un esquema de regresión, `validate_inputs` además rechaza vacíos en columnas que nunca los tuvieron y valores
nuevos en las categóricas de lista cerrada; en `warn_only_categories` (códigos de municipio) solo advierte.
Las funciones de clasificación (`predict_with_scores`, `decide_min_cost`) se conservan hasta la etapa 9 y se quitarán allí.


Contrato (el mismo que el del ejemplo del curso):
  - Entrada: una tabla con las columnas CRUDAS que una persona conoce al decidir (las del esquema).
  - Salida: la clase decidida, la probabilidad de cada clase y una señal de "revisar" cuando el modelo duda.
  - Nunca devuelve una predicción silenciosa con datos imposibles: lanza `InputValidationError`.

Uso:

    from proyecto.inference.predict import load_model, predict_with_scores
    from proyecto.inference.schema import load_schema
    model, schema = load_model("models/model.joblib"), load_schema("models/input_schema.json")
    resultado = predict_with_scores(filas_nuevas, model, schema)

Funciona con cualquier clasificador de scikit-learn (o un Pipeline) que tenga `predict_proba`.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class InputValidationError(ValueError):
    """Los datos de entrada no son válidos; el mensaje dice qué corregir."""


def load_model(path: str | Path):
    """Carga el modelo exportado (un Pipeline completo, con el preprocesamiento adentro)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe {path}. Ejecuta antes el notebook 09_inferencia para exportarlo.")
    return joblib.load(path)


def validate_inputs(df: pd.DataFrame, schema: dict) -> list[str]:
    """Valida columnas, tipos y rangos. Lanza InputValidationError si hay errores; devuelve advertencias."""
    numeric, categorical = schema["numeric"], schema["categorical"]
    missing = [c for c in numeric + categorical if c not in df.columns]
    if missing:
        raise InputValidationError(f"Faltan columnas: {', '.join(missing)}")

    errors, warnings = [], []
    regression = schema.get("task") == "regression"
    if regression:   # vacíos solo donde el entrenamiento los tuvo («sin respuesta»)
        nullable = set(schema.get("nullable", []))
        for col in numeric + categorical:
            if col not in nullable and df[col].isna().any():
                errors.append(f"{col}: no admite vacío (en el entrenamiento nunca estuvo vacío)")
    for col in numeric:
        values = pd.to_numeric(df[col], errors="coerce")
        if (values.isna() & df[col].notna()).any():
            errors.append(f"{col}: hay valores que no son números")
        if col in schema.get("valid_range", {}):
            low, high = schema["valid_range"][col]
            if (values.notna() & ~values.between(low, high)).any():
                errors.append(f"{col}: debe estar entre {low:g} y {high:g}")
    warn_only = set(schema.get("warn_only_categories", []))
    for col, known in schema.get("categories", {}).items():
        unseen = set(df[col].dropna().astype(str)) - set(known)
        if not unseen:
            continue
        message = f"{col}: categoría no vista en el entrenamiento ({', '.join(sorted(unseen))})"
        if regression and col not in warn_only:
            errors.append(message + "; elige uno de los valores válidos")   # lista cerrada: es un error de captura
        else:
            warnings.append(message)
    if errors:
        raise InputValidationError("; ".join(errors))

    for col, (low, high) in schema.get("observed_range", {}).items():
        values = pd.to_numeric(df[col], errors="coerce")
        if ((values < low) | (values > high)).any():
            warnings.append(f"{col}: fuera del rango visto en el entrenamiento ({low:g} a {high:g})")
    return warnings


def decide_min_cost(proba: np.ndarray, cost_matrix) -> np.ndarray:
    """Elige la clase de menor costo esperado: argmin_j sum_i p_i * costo(i, j)."""
    return np.argmin(proba @ np.asarray(cost_matrix, dtype=float), axis=1)


def _ordered_proba(model, X: pd.DataFrame, class_names: list[str]) -> np.ndarray:
    """Probabilidades en el orden de class_names (reordena si el modelo guarda sus clases con otro orden)."""
    proba = model.predict_proba(X)
    classes = getattr(model, "classes_", None)
    if classes is None and hasattr(model, "steps"):  # Pipeline
        classes = getattr(model.steps[-1][1], "classes_", None)
    if classes is not None:
        as_text = [str(c) for c in classes]
        if set(as_text) == set(class_names) and as_text != class_names:
            proba = proba[:, [as_text.index(name) for name in class_names]]
    return proba


def predict_with_scores(df: pd.DataFrame, model, schema: dict) -> pd.DataFrame:
    """Predice. Una fila de salida por fila de entrada.

    Columnas: decision, most_likely, proba_<clase>, needs_review y (si el esquema trae matriz de costos)
    expected_cost. Las advertencias de validación quedan en `resultado.attrs["warnings"]`.
    """
    warnings = validate_inputs(df, schema)
    class_names = schema["class_names"]
    proba = _ordered_proba(model, df, class_names)
    most_likely = proba.argmax(axis=1)

    cost = schema.get("cost_matrix")
    decision = decide_min_cost(proba, cost) if cost is not None else most_likely

    out = pd.DataFrame(proba, columns=[f"proba_{c}" for c in class_names], index=df.index)
    out.insert(0, "decision", [class_names[i] for i in decision])
    out["most_likely"] = [class_names[i] for i in most_likely]
    if cost is not None:
        out["expected_cost"] = (proba @ np.asarray(cost, dtype=float))[np.arange(len(df)), decision]
    out["needs_review"] = (proba.max(axis=1) < schema.get("review_threshold", 0.55)) | (decision != most_likely)
    out.attrs["warnings"] = warnings
    return out


def predict_score(df: pd.DataFrame, model, schema: dict) -> pd.DataFrame:
    """Regresión: valida contra el esquema y devuelve `puntaje_estimado` (una fila por fila de entrada).

    No calcula nada a partir de `df`: cada fila se predice con el modelo ya entrenado, sin redondear ni recortar.
    Las advertencias de validación quedan en `resultado.attrs["warnings"]`.
    """
    warnings = validate_inputs(df, schema)
    X = df[schema["numeric"] + schema["categorical"]]
    out = pd.DataFrame({"puntaje_estimado": model.predict(X)}, index=df.index)
    out.attrs["warnings"] = warnings
    return out
