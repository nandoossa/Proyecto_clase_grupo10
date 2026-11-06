"""Pruebas de evaluation.py: segmentos de equidad, tabla de equidad, diferencia de métricas por sede e importancia.

Todo con datos inventados; ninguna prueba lee `test.joblib`.
"""
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

from proyecto.data.split import GROUP_COL
from proyecto.models.evaluation import (
    bootstrap_metric_difference,
    equity_segments,
    equity_table,
    model_columns,
    permutation_importance_table,
    stratum_segment,
)
from proyecto.models.train import TARGET, build_pipeline, feature_frame


def test_stratum_segment_labels():
    df = pd.DataFrame({
        "fami_estratovivienda": [1.0, 6.0, np.nan, np.nan, 3.0],
        "sin_estrato": [0, 0, 1, 0, 0],
    })
    assert list(stratum_segment(df)) == ["Estrato 1", "Estrato 6", "Sin Estrato", "Sin dato (vacío)", "Estrato 3"]
    assert "Estrato 0" not in set(stratum_segment(df))


def test_equity_segments_columns_and_missing():
    df = pd.DataFrame({
        "fami_estratovivienda": [2.0, np.nan], "sin_estrato": [0, 1],
        "cole_area_ubicacion": ["URBANO", "RURAL"], "cole_naturaleza": ["OFICIAL", None], "estu_genero": [None, "M"],
    })
    seg = equity_segments(df)
    assert list(seg.columns) == ["estrato", "zona", "naturaleza", "genero"]
    assert seg.loc[1, "naturaleza"] == "Sin dato (vacío)" and seg.loc[0, "genero"] == "Sin dato (vacío)"
    assert seg.loc[1, "estrato"] == "Sin Estrato"


def test_metric_difference_point_value_and_groups():
    rng = np.random.default_rng(3)
    y = rng.normal(250, 40, 300)
    a, b = y + rng.normal(0, 10, 300), y + rng.normal(0, 25, 300)
    groups = np.repeat(np.arange(30), 10)
    for fn in (root_mean_squared_error, r2_score, mean_absolute_error):
        diff, low, high = bootstrap_metric_difference(y, a, b, groups, fn, n_boot=200)
        assert diff == pytest.approx(fn(y, a) - fn(y, b))
        assert low <= diff <= high
    assert bootstrap_metric_difference(y, a, a, groups, root_mean_squared_error, n_boot=50) == (0.0, 0.0, 0.0)
    # una sola sede: remuestrear sedes siempre da la misma muestra → intervalo sin ancho
    diff, low, high = bootstrap_metric_difference(y, a, b, np.zeros(300), root_mean_squared_error, n_boot=50)
    assert low == pytest.approx(diff) and high == pytest.approx(diff)


def test_equity_table_counts_and_rule():
    n_per = 20
    y = np.full(4 * n_per, 250.0)
    # segmento A: modelo mucho mejor; B: modelo apenas mejor en promedio (29,75 frente a 30) pero muy distinto entre sus
    # 4 sedes (5, 55, 9 y 50 puntos de error); C: empate exacto; D: modelo peor
    base = y + np.r_[np.full(n_per, 40.0), np.full(n_per, 30.0), np.full(n_per, 10.0), np.full(n_per, 5.0)]
    model = y + np.r_[np.full(n_per, 5.0), np.repeat([5.0, 55.0, 9.0, 50.0], 5), np.full(n_per, -10.0), np.full(n_per, 9.0)]
    segments = pd.DataFrame({"grupo": np.repeat(["A", "B", "C", "D"], n_per)})
    groups = np.r_[np.repeat(np.arange(10), 2), np.repeat(np.arange(10, 14), 5), np.repeat([20, 21], 10), np.full(n_per, 30)]
    table = equity_table(y, model, base, segments, groups, n_boot=300).loc["grupo"]

    assert list(table["estudiantes"]) == [n_per] * 4
    assert list(table["sedes"]) == [10, 4, 2, 1]
    assert table.loc["A", "mae_modelo"] == pytest.approx(5.0) and table.loc["A", "mae_linea_base"] == pytest.approx(40.0)
    assert table.loc["A", "diferencia"] == pytest.approx(-35.0)
    assert list(table["cumple"]) == [True, True, False, False]   # empate exacto (C) no cumple
    assert table.loc["A", "veredicto"] == "cumple con ventaja clara"
    assert table.loc["B", "veredicto"] == "cumple sin ventaja concluyente"
    assert table.loc["C", "veredicto"] == table.loc["D", "veredicto"] == "no cumple"


def test_model_columns_exclude_group_and_target():
    cols = model_columns()
    assert GROUP_COL not in cols and TARGET not in cols
    assert len(cols) == len(set(cols)) == 21


def test_permutation_importance_detects_signal(school_frame):
    df = school_frame(n_schools=40, per_school=10)   # el puntaje depende del estrato y de la edad
    X, y = feature_frame(df)
    pipe = build_pipeline(HistGradientBoostingRegressor(max_iter=50, random_state=0), scale=False).fit(X, y)
    table = permutation_importance_table(pipe, X, y, ["fami_estratovivienda", "cole_bilingue"], n_repeats=3)
    assert list(table.columns) == ["aumento_mae", "desviacion"]
    assert table.loc["fami_estratovivienda", "aumento_mae"] > 5          # define el puntaje
    assert abs(table.loc["cole_bilingue", "aumento_mae"]) < 1           # no influye en el puntaje inventado
    assert table.index[0] == "fami_estratovivienda"                     # ordenada de mayor a menor


def test_permutation_importance_only_permutes_model_columns(school_frame, monkeypatch):
    """H8 (auditoría de la etapa 7): la función quita de X lo que el modelo no usa (la sede) antes de permutar."""
    import proyecto.models.evaluation as evaluation

    X, y = feature_frame(school_frame(n_schools=20, per_school=5))
    pipe = build_pipeline(HistGradientBoostingRegressor(max_iter=10, random_state=0), scale=False).fit(X, y)
    seen = {}
    original = evaluation.permutation_importance

    def spy(estimator, X_perm, *args, **kwargs):
        seen["columns"] = list(X_perm.columns)
        return original(estimator, X_perm, *args, **kwargs)

    monkeypatch.setattr(evaluation, "permutation_importance", spy)
    table = permutation_importance_table(pipe, X, y, ["fami_estratovivienda", "edad"], n_repeats=2)
    assert seen["columns"] == model_columns() and GROUP_COL not in seen["columns"]
    assert sorted(table.index) == ["edad", "fami_estratovivienda"]          # se pueden pedir solo algunas


def test_permutation_importance_same_result_with_extra_columns(school_frame):
    """Filtrar dentro no cambia el resultado: pasar X completo (con la sede) da lo mismo que pasar X ya filtrado,
    que es como lo llamó el notebook 07. scikit-learn usa una sola semilla para todas las columnas."""
    X, y = feature_frame(school_frame(n_schools=30, per_school=6))
    pipe = build_pipeline(HistGradientBoostingRegressor(max_iter=20, random_state=0), scale=False).fit(X, y)
    cols = model_columns()
    assert GROUP_COL in X.columns and GROUP_COL not in cols
    filtered = permutation_importance_table(pipe, X[cols], y, cols, n_repeats=3)
    full = permutation_importance_table(pipe, X, y, cols, n_repeats=3)
    pd.testing.assert_frame_equal(filtered, full)
