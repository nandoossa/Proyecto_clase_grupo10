"""Pruebas del esquema y de la inferencia de regresión, con modelos de juguete y, si está, el modelo real.

Desde la etapa 9, `predict.py` solo tiene la regresión: las funciones de clasificación de la plantilla se quitaron. Las
pruebas de `build_schema` con clases se conservan porque `schema.py` no cambió en esta etapa.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from proyecto.inference import predict
from proyecto.inference.predict import InputValidationError, predict_score, validate_inputs
from proyecto.inference.schema import build_schema, load_schema

NUMERIC, CATEGORICAL, CLASSES = ["edad", "ingreso"], ["ciudad"], ["bajo", "alto"]
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def data() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 200
    df = pd.DataFrame({
        "edad": rng.integers(18, 70, n),
        "ingreso": rng.normal(2000, 500, n).round(1),
        "ciudad": rng.choice(["norte", "sur", "centro"], n),
    })
    df["y"] = ((df["ingreso"] > 2000) & (df["edad"] > 35)).astype(int)
    return df


def make_schema(data, **kwargs) -> dict:
    return build_schema(data, NUMERIC, CATEGORICAL, CLASSES, valid_range={"edad": (0, 120)}, **kwargs)


def test_build_schema_saves_and_reloads(data, tmp_path):
    path = tmp_path / "input_schema.json"
    schema = make_schema(data, path=path)
    assert path.exists() and load_schema(path) == json.loads(path.read_text(encoding="utf-8"))
    assert schema["numeric"] == NUMERIC and schema["class_names"] == CLASSES
    assert set(schema["categories"]["ciudad"]) == {"norte", "sur", "centro"}
    assert "edad" in schema["integer_columns"] and "ingreso" not in schema["integer_columns"]
    assert schema["observed_range"]["edad"][0] >= 18


def test_build_schema_rejects_bad_cost_matrix(data):
    with pytest.raises(ValueError, match="cost_matrix"):
        make_schema(data, cost_matrix=[[0, 1, 2], [1, 0, 2]])


def test_build_schema_rejects_missing_column(data):
    with pytest.raises(ValueError, match="Faltan columnas"):
        build_schema(data.drop(columns=["ingreso"]), NUMERIC, CATEGORICAL, CLASSES)


def test_classification_functions_removed():
    """Etapa 9: `predict.py` queda solo con la regresión."""
    for name in ("predict_with_scores", "decide_min_cost", "_ordered_proba"):
        assert not hasattr(predict, name), f"{name} debía quitarse en la etapa 9"


def test_validate_requires_regression_schema(data):
    """Un esquema de clasificación ya no se acepta: el error lo dice en vez de validar a medias."""
    row = pd.DataFrame([{"edad": 40, "ingreso": 2500.0, "ciudad": "norte"}])
    with pytest.raises(InputValidationError, match="regresión"):
        validate_inputs(row, make_schema(data))


# --- Regresión (etapa 8): esquema y predicción del puntaje -------------------------------------------------------------
# Datos inventados: `edad` y `ciudad` tienen vacíos en el entrenamiento (admiten «sin respuesta»); `ingreso` y `colegio`
# no. `municipio` es un código: si llega uno no visto, solo se advierte.
R_NUM, R_CAT = ["edad", "ingreso"], ["ciudad", "colegio", "municipio"]


@pytest.fixture(scope="module")
def reg_data() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    n = 300
    df = pd.DataFrame({
        "edad": rng.integers(15, 25, n).astype(float),
        "ingreso": rng.normal(2000, 400, n).round(1),
        "ciudad": rng.choice(["norte", "sur", "centro"], n).astype(object),
        "colegio": rng.choice(["OFICIAL", "NO OFICIAL"], n),
        "municipio": rng.choice([5001, 5088, 5360], n),
    })
    df.loc[:9, "edad"] = np.nan
    df.loc[10:19, "ciudad"] = np.nan
    df["y"] = 250 + 0.02 * (df["ingreso"] - 2000) - 2 * df["edad"].fillna(18) + rng.normal(0, 5, n)
    return df


@pytest.fixture(scope="module")
def reg_model(reg_data) -> Pipeline:
    prep = ColumnTransformer([
        ("num", SimpleImputer(strategy="median", add_indicator=True), R_NUM),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="sin respuesta")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), R_CAT),
    ])
    return Pipeline([("prep", prep), ("model", LinearRegression())]).fit(reg_data[R_NUM + R_CAT], reg_data["y"])


def reg_schema(df, **kwargs) -> dict:
    return build_schema(df, R_NUM, R_CAT, task="regression", valid_range={"edad": (13, 80)},
                        warn_only_categories=["municipio"], **kwargs)


def reg_row(**overrides) -> pd.DataFrame:
    base = {"edad": 17.0, "ingreso": 2100.0, "ciudad": "sur", "colegio": "OFICIAL", "municipio": 5001}
    base.update(overrides)
    return pd.DataFrame([base])


def test_regression_schema_saves_and_reloads(reg_data, tmp_path):
    path = tmp_path / "input_schema.json"
    schema = reg_schema(reg_data, path=path)
    assert load_schema(path) == schema
    assert schema["task"] == "regression" and "class_names" not in schema
    assert schema["numeric"] == R_NUM and schema["categorical"] == R_CAT
    assert schema["categories"]["colegio"] == ["NO OFICIAL", "OFICIAL"]
    assert schema["categories"]["municipio"] == ["5001", "5088", "5360"]
    assert sorted(schema["nullable"]) == ["ciudad", "edad"]          # solo los que tenían vacíos
    assert schema["valid_range"]["edad"] == [13.0, 80.0]


def test_schema_median_comes_only_from_given_frame(reg_data):
    schema = reg_schema(reg_data)
    assert schema["median"]["ingreso"] == pytest.approx(float(reg_data["ingreso"].median()))
    other = reg_data.assign(ingreso=reg_data["ingreso"] + 1000)
    assert reg_schema(other)["median"]["ingreso"] == pytest.approx(schema["median"]["ingreso"] + 1000)


def test_predict_score_returns_one_number_per_row(reg_data, reg_model):
    rows = pd.concat([reg_row(), reg_row(edad=20.0)], ignore_index=True)
    result = predict_score(rows, reg_model, reg_schema(reg_data))
    assert list(result.columns) == ["puntaje_estimado"] and len(result) == 2
    assert np.isfinite(result["puntaje_estimado"]).all()
    assert result["puntaje_estimado"].iloc[0] == reg_model.predict(reg_row()[R_NUM + R_CAT])[0]   # sin redondear


def test_predict_score_rejects_missing_column(reg_data, reg_model):
    with pytest.raises(InputValidationError, match="ingreso"):
        predict_score(reg_row().drop(columns=["ingreso"]), reg_model, reg_schema(reg_data))


def test_predict_score_rejects_out_of_valid_range(reg_data, reg_model):
    for age in (12.0, 81.0):
        with pytest.raises(InputValidationError, match="edad"):
            predict_score(reg_row(edad=age), reg_model, reg_schema(reg_data))


def test_predict_score_rejects_non_numeric(reg_data, reg_model):
    with pytest.raises(InputValidationError, match="ingreso"):
        predict_score(reg_row(ingreso="mucho"), reg_model, reg_schema(reg_data))


def test_predict_score_accepts_missing_only_where_training_had_it(reg_data, reg_model):
    schema = reg_schema(reg_data)
    assert len(predict_score(reg_row(edad=np.nan, ciudad=np.nan), reg_model, schema)) == 1   # «sin respuesta»
    with pytest.raises(InputValidationError, match="ingreso"):
        predict_score(reg_row(ingreso=np.nan), reg_model, schema)                           # nunca tuvo vacíos
    with pytest.raises(InputValidationError, match="colegio"):
        predict_score(reg_row(colegio=np.nan), reg_model, schema)


def test_predict_score_rejects_unknown_closed_category_but_warns_on_municipality(reg_data, reg_model):
    schema = reg_schema(reg_data)
    with pytest.raises(InputValidationError, match="colegio"):
        predict_score(reg_row(colegio="PRIVADO"), reg_model, schema)
    result = predict_score(reg_row(municipio=5999), reg_model, schema)
    assert any("municipio" in w for w in result.attrs["warnings"])


def test_predict_score_does_not_learn_from_input(reg_data, reg_model):
    """Cada fila se predice sola: las otras filas del lote no cambian su puntaje, y el esquema no se modifica."""
    schema = reg_schema(reg_data)
    before = json.dumps(schema, sort_keys=True)
    alone = predict_score(reg_row(), reg_model, schema)["puntaje_estimado"].iloc[0]
    batch = pd.concat([reg_row(), reg_row(edad=np.nan, ingreso=9000.0), reg_row(ciudad=np.nan)], ignore_index=True)
    assert predict_score(batch, reg_model, schema)["puntaje_estimado"].iloc[0] == alone
    assert json.dumps(schema, sort_keys=True) == before


def test_real_model_predicts_a_training_row():
    """Con el modelo exportado y una fila real del entrenamiento (se salta si los archivos no están en este equipo)."""
    model_path, schema_path = ROOT / "models" / "model.joblib", ROOT / "models" / "input_schema.json"
    train_path = ROOT / "data" / "processed" / "train.joblib"
    if not (model_path.exists() and schema_path.exists() and train_path.exists()):
        pytest.skip("faltan models/model.joblib, models/input_schema.json o data/processed/train.joblib")
    import joblib

    from proyecto.inference.predict import load_model
    schema = load_schema(schema_path)
    row = joblib.load(train_path)[schema["numeric"] + schema["categorical"]].head(1)
    result = predict_score(row, load_model(model_path), schema)
    assert 100 <= result["puntaje_estimado"].iloc[0] <= 477


# --- Pruebas agregadas tras la revisión de la app (6 nov 2026) --------------------------------------------------------
# Cubren funciones públicas de `inference/` que no tenían prueba directa: `form.options`, `predict.load_model`,
# `predict.validate_inputs` (llamada sin pasar por `predict_score`) y `schema.save_schema` / `load_schema`.
from proyecto.inference import form
from proyecto.inference.schema import save_schema

REAL_SCHEMA_PATH = ROOT / "models" / "input_schema.json"


@pytest.fixture(scope="module")
def real_schema() -> dict:
    if not REAL_SCHEMA_PATH.exists():
        pytest.skip("falta models/input_schema.json")
    return load_schema(REAL_SCHEMA_PATH)


def test_options_offers_sin_respuesta_only_for_nullable_fields(real_schema):
    """Un campo que admite vacío ofrece «Sin respuesta» al final; uno que no lo admite, no."""
    nullable_field = "cole_bilingue"          # en schema["nullable"]
    required_field = "cole_naturaleza"        # fuera de schema["nullable"]
    assert nullable_field in real_schema["nullable"] and required_field not in real_schema["nullable"]
    with_blank = form.options(nullable_field, real_schema)
    assert with_blank[-1] == form.SIN_RESPUESTA == "Sin respuesta"
    assert with_blank[:-1] == list(real_schema["categories"][nullable_field])
    without_blank = form.options(required_field, real_schema)
    assert form.SIN_RESPUESTA not in without_blank
    assert without_blank == list(real_schema["categories"][required_field])


def test_options_stratum_offers_sin_estrato(real_schema):
    """El estrato ofrece 1 a 6 y «Sin estrato»; «Sin respuesta» solo si `fami_estratovivienda` admite vacío."""
    result = form.options(form.STRATUM_FIELD, real_schema)
    assert result[:7] == ["1", "2", "3", "4", "5", "6", "Sin estrato"]
    assert ("fami_estratovivienda" in real_schema["nullable"]) == (form.SIN_RESPUESTA in result)


def test_options_stratum_without_blank_when_not_nullable():
    """Esquema mínimo a mano: si el estrato no admite vacío, solo quedan 1 a 6 y «Sin estrato»."""
    result = form.options(form.STRATUM_FIELD, {"nullable": [], "categories": {}})
    assert result == ["1", "2", "3", "4", "5", "6", "Sin estrato"]
    with_blank = form.options(form.STRATUM_FIELD, {"nullable": ["fami_estratovivienda"], "categories": {}})
    assert with_blank == result + ["Sin respuesta"]


def test_load_model_missing_path_raises_file_not_found(tmp_path):
    """Una ruta que no existe lanza FileNotFoundError con un mensaje que dice cuál era."""
    missing = tmp_path / "no_existe.joblib"
    with pytest.raises(FileNotFoundError, match="no_existe.joblib"):
        predict.load_model(missing)


def test_validate_inputs_valid_row_returns_no_warnings(reg_data):
    """Fila normal: dentro de lo observado, categorías conocidas, sin vacíos prohibidos."""
    assert validate_inputs(reg_row(), reg_schema(reg_data)) == []


def test_validate_inputs_outside_observed_but_inside_valid_range_only_warns(reg_data):
    """Edad 30: el entrenamiento solo vio 15 a 24, pero 30 es posible (13 a 80). Advierte y no lanza error."""
    schema = reg_schema(reg_data)
    assert schema["observed_range"]["edad"][1] < 30 <= schema["valid_range"]["edad"][1]
    warnings = validate_inputs(reg_row(edad=30.0), schema)
    assert len(warnings) == 1 and "edad" in warnings[0] and "rango visto" in warnings[0]


def test_validate_inputs_unseen_municipality_only_warns(reg_data):
    """Un municipio no visto (y listado en warn_only_categories) da advertencia, no error."""
    warnings = validate_inputs(reg_row(municipio=5999), reg_schema(reg_data))
    assert len(warnings) == 1 and "municipio" in warnings[0] and "5999" in warnings[0]


def test_save_schema_then_load_schema_gives_same_dict(reg_data, tmp_path):
    """Guardar y volver a leer devuelve el mismo diccionario (también en una carpeta que aún no existe)."""
    schema = reg_schema(reg_data)
    path = tmp_path / "subcarpeta" / "esquema.json"
    save_schema(schema, path)
    assert path.exists()
    assert load_schema(path) == schema
