"""Pruebas de las variables y el preprocesador del modelo (etapa 4).

Las tablas se arman a mano con valores inventados para la prueba: no se usan filas reales.
"""
import numpy as np
import pandas as pd
import pytest

from proyecto.features.engineering import (
    FORBIDDEN_COLUMNS,
    NUMERIC_ENGINEERED,
    add_features,
    build_preprocessor,
    feature_columns,
)


def _frame(**kw) -> pd.DataFrame:
    """Cuatro estudiantes con todas las columnas de entrada (salida de la etapa 3)."""
    base = {
        "edad": [17.0, 18.0, np.nan, 16.0],
        "fami_estratovivienda": [2.0, 3.0, np.nan, 1.0],
        "sin_estrato": [0, 0, 1, 0],
        "fami_personashogar": [2.0, 3.0, 1.0, np.nan],
        "fami_cuartoshogar": [2.0, 3.0, 1.0, 2.0],
        "cole_area_ubicacion": ["URBANO", "RURAL", "URBANO", "URBANO"],
        "cole_bilingue": ["N", np.nan, "N", "S"],
        "cole_caracter": ["ACADÉMICO", "TÉCNICO", np.nan, "ACADÉMICO"],
        "cole_genero": ["MIXTO", "MIXTO", "FEMENINO", "MIXTO"],
        "cole_jornada": ["MAÑANA", "UNICA", "TARDE", "MAÑANA"],
        "cole_naturaleza": ["OFICIAL", "NO OFICIAL", "OFICIAL", "OFICIAL"],
        "cole_sede_principal": ["S", "S", "N", "S"],
        "estu_genero": ["F", "M", "F", "M"],
        "fami_educacionmadre": ["Secundaria (Bachillerato) completa", "No sabe", np.nan, "Postgrado"],
        "fami_educacionpadre": ["No sabe", "Primaria completa", np.nan, "No Aplica"],
        "fami_tieneautomovil": ["No", "Si", np.nan, "No"],
        "fami_tienecomputador": ["Si", "Si", np.nan, "No"],
        "fami_tieneinternet": ["Si", "No", np.nan, "Si"],
        "fami_tienelavadora": ["No", "Si", np.nan, "Si"],
        "cole_cod_mcpio_ubicacion": [5001, 5088, 5001, 5360],
        "estu_cod_reside_mcpio": [5001, 5001, 5001, np.nan],
        "cole_cod_dane_sede": [111, 222, 111, 333],
        "punt_global": [250, 300, 210, 280],
    }
    base.update(kw)
    return pd.DataFrame(base)


def _transform(prep, frame) -> pd.DataFrame:
    return pd.DataFrame(prep.transform(frame), columns=prep.get_feature_names_out())


# --- Historia 1: preprocesador base ---


def test_feature_columns_exclude_forbidden():
    for use_engineered in (False, True):
        numeric, categorical = feature_columns(use_engineered=use_engineered)
        assert not set(FORBIDDEN_COLUMNS) & set(numeric + categorical)
    for column in ("punt_global", "cole_cod_dane_sede", "estu_consecutivo", "estu_tipodocumento",
                   "estu_nacionalidad", "estu_privado_libertad"):
        assert column in FORBIDDEN_COLUMNS
    with pytest.raises(ValueError):
        feature_columns(extra_numeric=["punt_matematicas"])


def test_feature_columns_toggles():
    numeric_off, _ = feature_columns(use_engineered=False)
    numeric_on, _ = feature_columns(use_engineered=True)
    numeric_extra, _ = feature_columns(extra_numeric=["x"])
    assert not set(NUMERIC_ENGINEERED) & set(numeric_off)
    assert set(NUMERIC_ENGINEERED) <= set(numeric_on)
    assert "x" in numeric_extra


def test_preprocessor_ignores_forbidden_columns():
    frame = _frame(
        punt_ingles=[50, 60, 40, 55],
        estu_tipodocumento=["TI", "CC", "PEP", "TI"],
        estu_nacionalidad=["COLOMBIA", "VENEZUELA", "COLOMBIA", "COLOMBIA"],
        estu_privado_libertad=["N", "N", "S", "N"],
    )
    prep = build_preprocessor().fit(frame)
    names = " ".join(prep.get_feature_names_out())
    for column in ("punt_global", "punt_ingles", "cole_cod_dane_sede", "estu_tipodocumento",
                   "estu_nacionalidad", "estu_privado_libertad"):
        assert column not in names


def test_preprocessor_handles_unseen_category_and_missing():
    prep = build_preprocessor().fit(_frame())
    new = _frame().iloc[:2].copy()
    new["cole_cod_mcpio_ubicacion"] = [9999, np.nan]  # municipio nunca visto y vacío
    new["cole_jornada"] = ["NOCHE", np.nan]
    new["edad"] = [np.nan, 40.0]
    out = prep.transform(new)
    assert not np.isnan(out).any() and not np.isinf(out).any()


def test_sentinels_and_missing_are_separate_categories():
    prep = build_preprocessor(min_frequency=None).fit(_frame())
    names = list(prep.get_feature_names_out())
    assert "cat__fami_educacionmadre_No sabe" in names
    assert "cat__fami_educacionmadre_sin respuesta" in names


def test_numeric_missing_keeps_indicator():
    # Fila 3: edad vacía y «Sin Estrato» (estrato vacío y sin_estrato = 1).
    prep = build_preprocessor(scale=False).fit(_frame())
    out = _transform(prep, _frame())
    assert "num__missingindicator_edad" in out.columns
    assert "num__missingindicator_fami_estratovivienda" in out.columns
    assert out["num__sin_estrato"].tolist() == [0, 0, 1, 0]
    assert out.loc[2, "num__fami_estratovivienda"] == 2.0  # mediana de 1, 2 y 3, nunca 0


# --- Historia 2: variables nuevas ---


def test_add_features_does_not_mutate_input():
    frame = _frame()
    before = frame.copy()
    add_features(frame)
    pd.testing.assert_frame_equal(frame, before)


def test_n_bienes_hogar():
    out = add_features(_frame())
    assert out["n_bienes_hogar"].iloc[0] == 2  # computador e internet
    assert np.isnan(out["n_bienes_hogar"].iloc[2])  # no respondió ninguno: vacío, no 0


def test_educacion_max_padres():
    out = add_features(_frame())
    assert out["educacion_max_padres"].iloc[0] == 4  # secundaria completa; «No sabe» no cuenta
    assert out["educacion_max_padres"].iloc[1] == 2  # primaria completa; «No sabe» no cuenta
    assert np.isnan(out["educacion_max_padres"].iloc[2])  # ambos vacíos
    assert out["educacion_max_padres"].iloc[3] == 9  # postgrado; «No Aplica» no cuenta

    unknown = add_features(_frame(fami_educacionmadre=["No sabe"] * 4, fami_educacionpadre=["No Aplica"] * 4))
    assert unknown["educacion_max_padres"].isna().all()

    edge = add_features(_frame(
        fami_educacionmadre=["Técnica o tecnológica completa"] * 4,
        fami_educacionpadre=["Educación profesional incompleta"] * 4,
    ))
    assert (edge["educacion_max_padres"] == 7).all()  # escala confirmada por el grupo


def test_division_by_zero_or_missing_gives_nan_not_inf():
    out = add_features(_frame(fami_cuartoshogar=[0.0, np.nan, 1.0, 2.0]))
    assert np.isnan(out["personas_por_cuarto"].iloc[0])  # 0 cuartos
    assert np.isnan(out["personas_por_cuarto"].iloc[1])  # cuartos vacío
    assert np.isnan(out["personas_por_cuarto"].iloc[3])  # personas vacío
    assert not np.isinf(out.select_dtypes("number").to_numpy(dtype=float)).any()


def test_personas_por_cuarto():
    out = add_features(_frame())
    assert out["personas_por_cuarto"].iloc[0] == 3.5 / 2  # «3 a 4» en 2 cuartos
    assert out["personas_por_cuarto"].iloc[2] == 1.5  # «1 a 2» en 1 cuarto


def test_vive_en_mcpio_colegio():
    out = add_features(_frame())
    assert out["vive_en_mcpio_colegio"].iloc[0] == 1
    assert out["vive_en_mcpio_colegio"].iloc[1] == 0
    assert np.isnan(out["vive_en_mcpio_colegio"].iloc[3])  # municipio de residencia vacío


def test_preprocessor_with_engineered_features():
    prep = build_preprocessor(use_engineered=True).fit(add_features(_frame()))
    out = prep.transform(add_features(_frame()))
    assert not np.isnan(out).any() and not np.isinf(out).any()
