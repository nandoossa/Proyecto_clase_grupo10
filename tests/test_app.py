"""Pruebas de la etapa 9: el formulario (texto -> 21 columnas del modelo) y la app de Streamlit con AppTest.

Las pruebas de `form_to_row` usan el esquema real (`models/input_schema.json`); las de AppTest, además, el modelo
exportado. Si faltan en el equipo, se saltan. Los perfiles son inventados: no salen de los datos.
"""
import math
from pathlib import Path

import pandas as pd
import pytest

from proyecto.inference.form import (
    SIN_ESTRATO,
    SIN_RESPUESTA,
    TYPICAL_ERROR,
    display_value,
    form_to_row,
    reference_range,
)
from proyecto.inference.predict import InputValidationError
from proyecto.inference.schema import load_schema

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "streamlit_app.py"
SCHEMA_PATH = ROOT / "models" / "input_schema.json"
MODEL_PATH = ROOT / "models" / "model.joblib"

# Perfil inventado y válido, con los textos que ve la persona en el formulario.
PROFILE = {
    "cole_cod_mcpio_ubicacion": "5001",
    "cole_naturaleza": "OFICIAL",
    "cole_area_ubicacion": "URBANO",
    "cole_jornada": "MAÑANA",
    "cole_caracter": "ACADÉMICO",
    "cole_genero": "MIXTO",
    "cole_bilingue": "N",
    "cole_sede_principal": "S",
    "edad": 17,
    "estu_genero": "F",
    "estu_cod_reside_mcpio": "5001",
    "estrato": "2",
    "fami_personashogar": "3 a 4",
    "fami_cuartoshogar": "Tres",
    "fami_educacionmadre": "Secundaria (Bachillerato) completa",
    "fami_educacionpadre": "Primaria completa",
    "fami_tieneautomovil": "No",
    "fami_tienecomputador": "Si",
    "fami_tieneinternet": "Si",
    "fami_tienelavadora": "Si",
}
# Campos del formulario que admiten «Sin respuesta» (los 12 `nullable` del esquema; el estrato cubre dos columnas).
NULLABLE_FIELDS = [
    "edad", "estrato", "fami_personashogar", "fami_cuartoshogar", "cole_bilingue", "cole_caracter",
    "fami_educacionmadre", "fami_educacionpadre", "fami_tieneautomovil", "fami_tienecomputador",
    "fami_tieneinternet", "fami_tienelavadora",
]


@pytest.fixture(scope="module")
def schema() -> dict:
    if not SCHEMA_PATH.exists():
        pytest.skip("falta models/input_schema.json")
    return load_schema(SCHEMA_PATH)


def answers(**overrides) -> dict:
    out = dict(PROFILE)
    out.update(overrides)
    return out


# --- form_to_row: de los textos del formulario a la fila del modelo ------------------------------------------------------

def test_form_to_row_builds_the_21_model_columns(schema):
    row = form_to_row(answers(), schema)
    assert list(row.columns) == schema["numeric"] + schema["categorical"] and len(row) == 1
    first = row.iloc[0]
    assert first["edad"] == 17 and first["fami_estratovivienda"] == 2 and first["sin_estrato"] == 0
    assert first["fami_personashogar"] == 2 and first["fami_cuartoshogar"] == 3   # «3 a 4» -> 2, «Tres» -> 3
    assert first["cole_jornada"] == "MAÑANA" and first["cole_cod_mcpio_ubicacion"] == "5001"


def test_household_text_maps_to_stage3_codes(schema):
    for text, code in [("1 a 2", 1), ("9 o más", 5)]:
        assert form_to_row(answers(fami_personashogar=text), schema).iloc[0]["fami_personashogar"] == code
    for text, code in [("Uno", 1), ("Seis o mas", 6)]:
        assert form_to_row(answers(fami_cuartoshogar=text), schema).iloc[0]["fami_cuartoshogar"] == code


def test_stratum_rule_7b(schema):
    """«Sin estrato» -> estrato vacío y sin_estrato = 1; «Sin respuesta» -> estrato vacío y sin_estrato = 0."""
    sin_estrato = form_to_row(answers(estrato=SIN_ESTRATO), schema).iloc[0]
    assert math.isnan(sin_estrato["fami_estratovivienda"]) and sin_estrato["sin_estrato"] == 1
    vacio = form_to_row(answers(estrato=SIN_RESPUESTA), schema).iloc[0]
    assert math.isnan(vacio["fami_estratovivienda"]) and vacio["sin_estrato"] == 0


def test_sin_respuesta_gives_empty_values_where_allowed(schema):
    row = form_to_row(answers(**{field: SIN_RESPUESTA for field in NULLABLE_FIELDS}), schema)
    assert row[schema["nullable"]].isna().all(axis=None)


@pytest.mark.parametrize("age", [12, 81, 17.5])
def test_invalid_age_is_refused_with_a_correction(schema, age):
    with pytest.raises(InputValidationError, match="Edad"):
        form_to_row(answers(edad=age), schema)


def test_empty_age_asks_for_a_value_or_sin_respuesta(schema):
    with pytest.raises(InputValidationError, match="Edad"):
        form_to_row(answers(edad=None), schema)


def test_missing_required_field_names_it(schema):
    with pytest.raises(InputValidationError, match="Jornada del colegio"):
        form_to_row(answers(cole_jornada=None), schema)


def test_sin_respuesta_is_refused_in_required_fields(schema):
    with pytest.raises(InputValidationError, match="Género del estudiante"):
        form_to_row(answers(estu_genero=SIN_RESPUESTA), schema)


def test_reference_range_is_estimate_plus_minus_33_clipped():
    assert TYPICAL_ERROR == 33
    assert reference_range(250.4) == (217, 283)
    assert reference_range(110.0) == (100, 143) and reference_range(470.0) == (437, 477)


def test_municipality_shows_name_and_code_when_known():
    schema = {"municipality_names": {"5001": "MEDELLÍN"}}
    assert display_value("cole_cod_mcpio_ubicacion", "5001", schema) == "MEDELLÍN (5001)"
    assert display_value("cole_cod_mcpio_ubicacion", "5999", schema) == "5999"
    assert display_value("estu_genero", "F", schema) == "Femenino"


# --- App con AppTest -----------------------------------------------------------------------------------------------------

def run_app(profile: dict | None = None):
    """Abre la app; si se da un perfil, llena el formulario y pulsa «Estimar»."""
    if not (MODEL_PATH.exists() and SCHEMA_PATH.exists()):
        pytest.skip("faltan models/model.joblib o models/input_schema.json")
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(APP), default_timeout=60).run()
    if profile is None:
        return at
    for field, value in profile.items():
        if field == "edad":
            if value == SIN_RESPUESTA:
                at.checkbox(key="edad_sin_respuesta").check()
            else:
                at.number_input(key="edad").set_value(value)
        else:
            at.selectbox(key=field).set_value(value)
    at.button[0].click()
    return at.run()


def all_text(at) -> str:
    return " ".join(e.value for kind in ("markdown", "info", "warning", "caption", "success") for e in getattr(at, kind))


def test_app_loads_with_title_and_responsible_use():
    at = run_app()
    assert not at.exception
    assert at.title[0].value == "Predictor de resultados Pruebas Saber 11 en Antioquia"
    text = all_text(at)
    assert "39,57" in text and "35,74" in text and "31,40" in text   # estrato 5 y brecha por género (ficha)
    assert len(at.metric) == 0                                       # sin estimación antes de pulsar


def test_normal_profile_shows_rounded_score_and_typical_error():
    at = run_app(answers())
    assert not at.exception and not at.error
    score = at.metric[0].value
    assert score.isdigit() and 100 <= int(score) <= 477
    assert "se equivoca en promedio 33 puntos; como referencia, entre" in all_text(at)
    assert "no es un intervalo de confianza" in all_text(at)


def test_sin_respuesta_in_all_nullable_fields_still_predicts():
    at = run_app(answers(**{field: SIN_RESPUESTA for field in NULLABLE_FIELDS}))
    assert not at.exception and not at.error and len(at.metric) == 1


@pytest.mark.parametrize("age", [12, 81])
def test_invalid_age_shows_correction_and_no_score(age):
    at = run_app(answers(edad=age))
    assert len(at.metric) == 0
    assert any("Edad" in e.value for e in at.error)


def test_missing_required_field_shows_correction_and_no_score():
    at = run_app(answers(cole_jornada=None))
    assert len(at.metric) == 0
    assert any("Jornada del colegio" in e.value for e in at.error)


def test_app_code_does_not_use_databricks():
    source = APP.read_text(encoding="utf-8").lower() + (ROOT / "src/proyecto/inference/form.py").read_text(encoding="utf-8").lower()
    for word in ("mlflow", "databricks", "token"):
        assert word not in source, f"la app no debe mencionar '{word}'"
