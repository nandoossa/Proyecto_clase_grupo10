"""Inferencia de regresión: validar las entradas y estimar el puntaje global de Saber 11.

`predict_score(df, model, schema)` devuelve `puntaje_estimado`, sin redondear ni recortar (el redondeo lo hace la app).
`validate_inputs` rechaza columnas faltantes, valores no numéricos, valores fuera del rango válido, vacíos en columnas que
nunca los tuvieron y valores nuevos en las categóricas de lista cerrada; en `warn_only_categories` (códigos de municipio)
solo advierte. Nunca devuelve una predicción silenciosa con datos imposibles: lanza `InputValidationError`.

Desde la etapa 9 solo queda la regresión: las funciones de clasificación de la plantilla (`predict_with_scores`,
`decide_min_cost`) se quitaron.

Uso:

    from proyecto.inference.predict import load_model, predict_score
    from proyecto.inference.schema import load_schema
    model, schema = load_model("models/model.joblib"), load_schema("models/input_schema.json")
    resultado = predict_score(filas_nuevas, model, schema)
"""
from pathlib import Path

import joblib
import pandas as pd


class InputValidationError(ValueError):
    """Los datos de entrada no son válidos; el mensaje dice qué corregir."""


def load_model(path: str | Path):
    """Carga el modelo exportado (un Pipeline completo, con el preprocesamiento adentro)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe {path}. Se exporta en el notebook 08_registro_modelo.")
    return joblib.load(path)


def validate_inputs(df: pd.DataFrame, schema: dict) -> list[str]:
    """Valida columnas, tipos y rangos. Lanza InputValidationError si hay errores; devuelve advertencias."""
    if schema.get("task") != "regression":
        raise InputValidationError("El esquema no es de regresión: este proyecto solo estima el puntaje global.")
    numeric, categorical = schema["numeric"], schema["categorical"]
    missing = [c for c in numeric + categorical if c not in df.columns]
    if missing:
        raise InputValidationError(f"Faltan columnas: {', '.join(missing)}")

    errors, warnings = [], []
    nullable = set(schema.get("nullable", []))   # vacíos solo donde el entrenamiento los tuvo («sin respuesta»)
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
        if col not in warn_only:
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
