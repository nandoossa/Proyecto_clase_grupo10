"""Formulario de la app (etapa 9): de lo que escribe una persona a la fila de 21 columnas que espera el modelo.

La persona ve textos en español («3 a 4», «Dos», «Sin estrato»); el modelo espera los códigos de la etapa 3. Aquí está esa
traducción, sin Streamlit, para que la usen la app y el notebook 09 y se pueda probar. Si algo no se puede traducir (una
edad imposible, un campo obligatorio vacío), `form_to_row` lanza `InputValidationError` con un mensaje que dice qué
corregir. Lo que no detecta aquí lo revisa después `predict_score` contra el esquema.
"""
import math

import numpy as np
import pandas as pd

from proyecto.data.cleaning import HOUSEHOLD_SIZE_CODES, ROOM_CODES
from proyecto.inference.predict import InputValidationError

SIN_RESPUESTA = "Sin respuesta"
SIN_ESTRATO = "Sin estrato"
STRATUM_FIELD = "estrato"   # un solo campo del formulario para `fami_estratovivienda` y `sin_estrato` (regla 7b)
# Cifra de la prueba en un solo sitio (revisión de la app, H9): si el modelo se reentrena, se cambia aquí y en la ficha.
TEST_MAE = 33.32            # MAE en la prueba (models/ficha_modelo.md, reports/07_metricas_test.json)
TYPICAL_ERROR = round(TEST_MAE)   # 33: lo que ve la persona («se equivoca en promedio 33 puntos»)
SCORE_RANGE = (100, 477)    # rango posible del puntaje global

# Etiquetas en español claro, en el orden y las secciones del formulario.
SECTIONS = {
    "Colegio": {
        "cole_cod_mcpio_ubicacion": "Municipio del colegio",
        "cole_naturaleza": "Naturaleza del colegio",
        "cole_area_ubicacion": "Zona del colegio",
        "cole_jornada": "Jornada del colegio",
        "cole_caracter": "Carácter del colegio",
        "cole_genero": "Población del colegio",
        "cole_bilingue": "¿El colegio es bilingüe?",
        "cole_sede_principal": "¿Es la sede principal?",
    },
    "Estudiante": {
        "edad": "Edad (años cumplidos)",
        "estu_genero": "Género del estudiante",
        "estu_cod_reside_mcpio": "Municipio donde vive el estudiante",
    },
    "Hogar": {
        STRATUM_FIELD: "Estrato de la vivienda",
        "fami_personashogar": "Personas que viven en el hogar",
        "fami_cuartoshogar": "Cuartos para dormir en el hogar",
        "fami_educacionmadre": "Nivel educativo de la madre",
        "fami_educacionpadre": "Nivel educativo del padre",
        "fami_tieneautomovil": "¿El hogar tiene automóvil?",
        "fami_tienecomputador": "¿El hogar tiene computador?",
        "fami_tieneinternet": "¿El hogar tiene internet?",
        "fami_tienelavadora": "¿El hogar tiene lavadora?",
    },
}
LABELS = {field: label for fields in SECTIONS.values() for field, label in fields.items()}
MUNICIPALITY_FIELDS = ("cole_cod_mcpio_ubicacion", "estu_cod_reside_mcpio")
# Cómo se muestran los valores que vienen en código o abreviados en los datos.
VALUE_LABELS = {
    "S": "Sí", "N": "No", "Si": "Sí", "No": "No", "F": "Femenino", "M": "Masculino",
    "UNICA": "ÚNICA", "Seis o mas": "Seis o más",
}
YES_NO_COLUMNS = ("cole_bilingue", "cole_sede_principal", "fami_tieneautomovil", "fami_tienecomputador",
                  "fami_tieneinternet", "fami_tienelavadora")


def options(field: str, schema: dict) -> list[str]:
    """Opciones de una lista del formulario (valores tal como los espera `form_to_row`)."""
    if field == STRATUM_FIELD:
        values = [str(i) for i in range(1, 7)] + [SIN_ESTRATO]
        nullable = "fami_estratovivienda" in schema["nullable"]
    else:
        if field == "fami_personashogar":
            values = list(HOUSEHOLD_SIZE_CODES)
        elif field == "fami_cuartoshogar":
            values = list(ROOM_CODES)
        else:
            values = list(schema["categories"][field])
        nullable = field in schema["nullable"]
    return values + [SIN_RESPUESTA] if nullable else values


def display_value(field: str, value, schema: dict) -> str:
    """Texto que ve la persona para un valor: «MEDELLÍN (5001)» en municipios, «Sí» en lugar de «S», etc."""
    value = str(value)
    if field in MUNICIPALITY_FIELDS:
        name = schema.get("municipality_names", {}).get(value)
        return f"{name} ({value})" if name else value
    if field == "estu_genero" or field in YES_NO_COLUMNS or value in ("UNICA", "Seis o mas"):
        return VALUE_LABELS.get(value, value)
    return value


def _required(field: str, value, errors: list[str], schema_nullable: bool):
    """Devuelve el valor o NaN («Sin respuesta»); anota un error si falta o si no admite «Sin respuesta»."""
    if value is None:
        errors.append(f"{LABELS[field]}: elige una opción.")
        return np.nan
    if value == SIN_RESPUESTA:
        if not schema_nullable:
            errors.append(f"{LABELS[field]}: este dato es obligatorio; elige una opción.")
        return np.nan
    return value


def _age(value, schema: dict, errors: list[str]) -> float:
    low, high = schema["valid_range"]["edad"]
    hint = f"escribe un número entero entre {low:g} y {high:g}, o marca «{SIN_RESPUESTA}»."
    if value == SIN_RESPUESTA:
        return np.nan
    if value is None:
        errors.append(f"{LABELS['edad']}: {hint}")
        return np.nan
    try:
        age = float(value)
    except (TypeError, ValueError):
        errors.append(f"{LABELS['edad']}: {hint}")
        return np.nan
    if math.isnan(age) or not age.is_integer() or not low <= age <= high:
        errors.append(f"{LABELS['edad']}: {hint}")
        return np.nan
    return age


def form_to_row(answers: dict, schema: dict) -> pd.DataFrame:
    """Traduce las respuestas del formulario a una fila con las 21 columnas del modelo.

    `answers` tiene una clave por campo del formulario (las de `LABELS`). Un valor `None` es «no eligió nada»;
    `SIN_RESPUESTA` es un vacío permitido. Si hay errores, los junta todos en un solo `InputValidationError`.
    """
    errors: list[str] = []
    nullable = set(schema["nullable"])
    row: dict = {"edad": _age(answers.get("edad"), schema, errors)}

    stratum = _required(STRATUM_FIELD, answers.get(STRATUM_FIELD), errors, "fami_estratovivienda" in nullable)
    if stratum == SIN_ESTRATO:            # regla 7b: estrato vacío y la marca aparte
        row["fami_estratovivienda"], row["sin_estrato"] = np.nan, 1.0
    else:
        row["fami_estratovivienda"] = np.nan if pd.isna(stratum) else float(stratum)
        row["sin_estrato"] = 0.0

    for field, codes in (("fami_personashogar", HOUSEHOLD_SIZE_CODES), ("fami_cuartoshogar", ROOM_CODES)):
        value = _required(field, answers.get(field), errors, field in nullable)
        row[field] = np.nan if pd.isna(value) else float(codes[value])

    for field in schema["categorical"]:
        value = _required(field, answers.get(field), errors, field in nullable)
        row[field] = np.nan if pd.isna(value) else str(value)

    if errors:
        raise InputValidationError(" ".join(errors))
    columns = schema["numeric"] + schema["categorical"]
    return pd.DataFrame([row])[columns].astype({c: float for c in schema["numeric"]})


def reference_range(score: float, typical_error: int = TYPICAL_ERROR) -> tuple[int, int]:
    """Estimación ± error típico, redondeada y recortada a 100–477. Es una referencia, NO un intervalo de confianza."""
    low, high = SCORE_RANGE
    return max(low, round(score - typical_error)), min(high, round(score + typical_error))
