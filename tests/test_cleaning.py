"""Pruebas de la limpieza (etapa 3). Una prueba por regla de `especificaciones/03-preprocesamiento.md`.

Las filas se arman a mano con el formato del CSV crudo y valores inventados: no se usan filas reales.
"""
import numpy as np
import pandas as pd

from proyecto.data.cleaning import (
    CONSTANT_COLUMNS,
    LEAKAGE_COLUMNS,
    PERSONAL_COLUMNS,
    SCHOOL_ID_COLUMNS,
    add_age_and_drop_personal,
    clean,
    drop_constant_columns,
    drop_exact_duplicates,
    drop_leakage_columns,
    drop_school_identifiers,
    encode_ordinal_columns,
    keep_calendar_a,
    mark_impossible_age,
)

_BASE_ROW = {
    "periodo": 20224,
    "estu_tipodocumento": "TI",
    "estu_consecutivo": "SB0000000001",
    "cole_area_ubicacion": "URBANO",
    "cole_bilingue": "N",
    "cole_calendario": "A",
    "cole_caracter": "ACADÉMICO",
    "cole_cod_dane_establecimiento": 105001000001,
    "cole_cod_dane_sede": 105001000101,
    "cole_cod_depto_ubicacion": 5,
    "cole_cod_mcpio_ubicacion": 5001,
    "cole_codigo_icfes": 10001,
    "cole_depto_ubicacion": "ANTIOQUIA",
    "cole_genero": "MIXTO",
    "cole_jornada": "MAÑANA",
    "cole_mcpio_ubicacion": "MEDELLÍN",
    "cole_naturaleza": "OFICIAL",
    "cole_nombre_establecimiento": "COLEGIO DE PRUEBA",
    "cole_nombre_sede": "SEDE DE PRUEBA",
    "cole_sede_principal": "S",
    "estu_cod_depto_presentacion": 5,
    "estu_cod_mcpio_presentacion": 5001,
    "estu_cod_reside_depto": 5,
    "estu_cod_reside_mcpio": 5001,
    "estu_depto_presentacion": "ANTIOQUIA",
    "estu_depto_reside": "ANTIOQUIA",
    "estu_estadoinvestigacion": "PUBLICAR",
    "estu_estudiante": "ESTUDIANTE",
    "estu_fechanacimiento": "14/01/2005",
    "estu_genero": "F",
    "estu_mcpio_presentacion": "MEDELLÍN",
    "estu_mcpio_reside": "MEDELLÍN",
    "estu_nacionalidad": "COLOMBIA",
    "estu_pais_reside": "COLOMBIA",
    "estu_privado_libertad": "N",
    "fami_cuartoshogar": "Tres",
    "fami_educacionmadre": "Secundaria (Bachillerato) completa",
    "fami_educacionpadre": "Primaria completa",
    "fami_estratovivienda": "Estrato 2",
    "fami_personashogar": "3 a 4",
    "fami_tieneautomovil": "No",
    "fami_tienecomputador": "Si",
    "fami_tieneinternet": "Si",
    "fami_tienelavadora": "Si",
    "desemp_ingles": "A1",
    "punt_ingles": 50,
    "punt_matematicas": 50,
    "punt_sociales_ciudadanas": 50,
    "punt_c_naturales": 50,
    "punt_lectura_critica": 50,
    "punt_global": 250,
}


def _raw(n: int = 1, **columns) -> pd.DataFrame:
    """`n` filas con el formato crudo (51 columnas); `columns` reemplaza columnas con una lista de `n` valores."""
    frame = pd.DataFrame([_BASE_ROW] * n)
    frame["estu_consecutivo"] = [f"SB{i:010d}" for i in range(n)]
    for name, values in columns.items():
        frame[name] = values
    return frame


def test_raw_helper_has_the_51_source_columns():
    assert _raw().shape == (1, 51)


def test_drop_exact_duplicates():
    frame = pd.concat([_raw(), _raw()], ignore_index=True)
    assert len(drop_exact_duplicates(frame)) == 1
    # Dos estudiantes distintos con las mismas respuestas no son duplicados.
    assert len(drop_exact_duplicates(_raw(2))) == 2


def test_drop_leakage_columns():
    out = drop_leakage_columns(_raw())
    assert not set(LEAKAGE_COLUMNS) & set(out.columns)
    assert len(LEAKAGE_COLUMNS) == 7
    assert "punt_global" in out.columns


def test_no_personal_columns():
    out = add_age_and_drop_personal(_raw(2, estu_fechanacimiento=["14/01/2001", "no es fecha"]))
    assert not set(PERSONAL_COLUMNS) & set(out.columns)
    assert out["edad"].iloc[0] == 21
    assert np.isnan(out["edad"].iloc[1])
    assert not set(PERSONAL_COLUMNS) & set(clean(_raw()).columns)


def test_mark_impossible_age():
    frame = pd.DataFrame({"edad": [12.0, 13.0, 80.0, np.nan]})
    out = mark_impossible_age(frame)
    assert len(out) == 4  # la fila se conserva
    assert np.isnan(out["edad"].iloc[0])
    assert out["edad"].iloc[1:3].tolist() == [13.0, 80.0]


def test_encode_ordinal_columns():
    out = encode_ordinal_columns(_raw(
        4,
        fami_personashogar=["9 o más", "1 a 2", np.nan, "texto raro"],
        fami_cuartoshogar=["Seis o mas", "Uno", np.nan, "Tres"],
        fami_estratovivienda=["Estrato 4", "Estrato 1", "Estrato 6", "Estrato 2"],
    ))
    assert out["fami_personashogar"].iloc[:2].tolist() == [5, 1]
    assert out["fami_personashogar"].iloc[2:].isna().all()  # vacío y texto no previsto -> vacío
    assert out["fami_cuartoshogar"].iloc[:2].tolist() == [6, 1] and np.isnan(out["fami_cuartoshogar"].iloc[2])
    assert out["fami_estratovivienda"].tolist() == [4, 1, 6, 2]


def test_sin_estrato_flag():
    out = encode_ordinal_columns(_raw(3, fami_estratovivienda=["Sin Estrato", np.nan, "Estrato 2"]))
    assert np.isnan(out["fami_estratovivienda"].iloc[0])  # vacío, nunca 0
    assert np.isnan(out["fami_estratovivienda"].iloc[1])
    assert out["fami_estratovivienda"].iloc[2] == 2
    assert out["sin_estrato"].tolist() == [1, 0, 0]
    assert (out["fami_estratovivienda"] != 0).all()


def test_sentinels_are_kept():
    out = clean(_raw(
        2,
        fami_educacionmadre=["No sabe", "No Aplica"],
        fami_educacionpadre=["No Aplica", "No sabe"],
    ))
    assert out["fami_educacionmadre"].tolist() == ["No sabe", "No Aplica"]
    assert out["fami_educacionpadre"].tolist() == ["No Aplica", "No sabe"]


def test_drop_constant_columns():
    out = drop_constant_columns(_raw())
    assert not set(CONSTANT_COLUMNS) & set(out.columns) and len(CONSTANT_COLUMNS) == 4


def test_drop_school_identifiers():
    out = drop_school_identifiers(_raw())
    assert not set(SCHOOL_ID_COLUMNS) & set(out.columns) and len(SCHOOL_ID_COLUMNS) == 4
    assert "cole_cod_dane_sede" in out.columns  # se conserva para agrupar


def test_keep_calendar_a():
    out = keep_calendar_a(_raw(3, cole_calendario=["A", "OTRO", "A"]))
    assert out["cole_calendario"].tolist() == ["A", "A"]


def test_clean_does_not_mutate_input():
    frame = _raw(3)
    before = frame.copy()
    clean(frame)
    pd.testing.assert_frame_equal(frame, before)


def test_clean_output_shape():
    # 51 columnas - 7 fuga - 2 personales - 4 constantes - 4 identificadores + edad + sin_estrato = 36
    frame = pd.concat([_raw(3), _raw(3).iloc[[0]]], ignore_index=True)  # una fila duplicada
    frame.loc[2, "cole_calendario"] = "OTRO"
    out = clean(frame)
    assert out.shape == (2, 36)


def test_clean_output_matches_feature_stage():
    from proyecto.features.engineering import add_features, build_preprocessor, feature_columns

    raw = _raw(
        6,
        fami_estratovivienda=["Estrato 1", "Estrato 3", "Sin Estrato", np.nan, "Estrato 6", "Estrato 2"],
        fami_personashogar=["1 a 2", "3 a 4", "5 a 6", "7 a 8", "9 o más", np.nan],
        fami_cuartoshogar=["Uno", "Dos", "Tres", "Cuatro", "Cinco", "Seis o mas"],
        fami_educacionmadre=["Ninguno", "No sabe", "Postgrado", np.nan, "Primaria completa", "No Aplica"],
        estu_fechanacimiento=["01/01/2005", "01/01/2004", "01/01/2015", "01/01/1990", "01/01/2005", "01/01/2006"],
        cole_cod_mcpio_ubicacion=[5001, 5088, 5001, 5360, 5001, 5088],
        estu_cod_reside_mcpio=[5001, 5001, 5001, 5360, 5088, 5088],
    )
    out = clean(raw)
    numeric, categorical = feature_columns(use_engineered=False)
    assert set(numeric + categorical + ["cole_cod_dane_sede"]) <= set(out.columns)
    assert set(out["fami_personashogar"].dropna()) <= {1, 2, 3, 4, 5}
    assert set(out["fami_cuartoshogar"].dropna()) <= {1, 2, 3, 4, 5, 6}
    assert set(out["fami_estratovivienda"].dropna()) <= {1, 2, 3, 4, 5, 6}
    assert set(out["sin_estrato"]) <= {0, 1}

    matrix = build_preprocessor(use_engineered=True).fit_transform(add_features(out))
    assert not np.isnan(matrix).any() and not np.isinf(matrix).any()
