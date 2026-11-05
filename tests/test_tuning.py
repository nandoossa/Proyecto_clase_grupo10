"""Pruebas de tuning.py: espacios de búsqueda, búsqueda reanudable, reserva de sedes y bootstrap por sede.

Las tablas se arman a mano con valores inventados (`_frame` de test_models.py) y modelos diminutos, para que corran rápido.
"""
import numpy as np
import optuna
import pandas as pd
import pytest
from sklearn.metrics import mean_absolute_error

from proyecto.data.split import GROUP_COL, group_cv
from proyecto.models.train import candidates, feature_frame
from proyecto.models.tuning import (
    MODELS,
    STARTING_PARAMS,
    bootstrap_mae_difference,
    bootstrap_metric_ci,
    build_tuned_pipeline,
    hgb_space,
    reserve_groups,
    tune,
    xgb_space,
)
from test_models import _frame

optuna.logging.set_verbosity(optuna.logging.WARNING)

# Rangos de especificaciones/06-optimizacion.md §4: (mínimo, máximo) o conjunto de opciones.
HGB_RANGES = {
    "min_frequency": {0.01, 0.001},
    "loss": {"squared_error", "absolute_error"},
    "learning_rate": (0.02, 0.2),
    "max_iter": (150, 600),
    "max_leaf_nodes": (15, 63),
    "min_samples_leaf": (20, 200),
    "l2_regularization": (1e-3, 10.0),
    "max_features": (0.5, 1.0),
}
XGB_RANGES = {
    "min_frequency": {0.01, 0.001},
    "objective": {"reg:squarederror", "reg:absoluteerror"},
    "learning_rate": (0.02, 0.2),
    "n_estimators": (150, 600),
    "max_depth": (3, 10),
    "min_child_weight": (1.0, 100.0),
    "subsample": (0.6, 1.0),
    "colsample_bytree": (0.5, 1.0),
    "reg_lambda": (1e-3, 10.0),
}


def _sample(space_fn, n: int = 20) -> list[dict]:
    """Parámetros de `n` ensayos al azar del espacio (sin entrenar nada)."""
    study = optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=0))
    out = []
    for _ in range(n):
        trial = study.ask()
        out.append(space_fn(trial))
        study.tell(trial, 0.0)
    return out


@pytest.mark.parametrize("space_fn, ranges", [(hgb_space, HGB_RANGES), (xgb_space, XGB_RANGES)])
def test_spaces_return_params_in_range(space_fn, ranges):
    for params in _sample(space_fn):
        assert set(params) == set(ranges)
        for name, allowed in ranges.items():
            if isinstance(allowed, set):
                assert params[name] in allowed, name
            else:
                assert allowed[0] <= params[name] <= allowed[1], name


def _tiny(params: dict, name: str) -> dict:
    """Mismos parámetros, con pocos árboles para que la prueba sea rápida."""
    small = dict(params)
    small["max_iter" if name == "hist gradient boosting" else "n_estimators"] = 10
    return small


@pytest.mark.parametrize("name", list(MODELS))
def test_factories_build_models_that_fit(name):
    X, y = feature_frame(_frame())
    space_fn, _ = MODELS[name]
    for params in [_sample(space_fn, 1)[0], STARTING_PARAMS[name]]:
        pipe = build_tuned_pipeline(name, _tiny(params, name)).fit(X, y)
        pred = pipe.predict(X)
        assert len(pred) == len(X) and not np.isnan(pred).any()
        # el umbral de poco frecuentes llega al preprocesador, no al modelo
        encoders = [t for _, t, _ in pipe.named_steps["prep"].transformers_ if hasattr(t, "named_steps")]
        onehots = [s for e in encoders for s in e.named_steps.values() if hasattr(s, "min_frequency")]
        assert onehots and all(o.min_frequency == params["min_frequency"] for o in onehots)


@pytest.mark.parametrize("name", list(MODELS))
def test_starting_params_match_tournament(name):
    _, make_fn = MODELS[name]
    built = make_fn(STARTING_PARAMS[name]).get_params()
    tournament = candidates()[name][0].get_params()
    for key, value in built.items():
        both_nan = isinstance(value, float) and np.isnan(value) and np.isnan(tournament[key])  # `missing` de XGBoost
        assert both_nan or tournament[key] == value, key
    assert STARTING_PARAMS[name]["min_frequency"] == 0.01


def test_tune_minimizes_mae_and_resumes(tmp_path):
    X, y = feature_frame(_frame())
    storage = tmp_path / "estudio.db"
    space_fn, make_fn = MODELS["xgboost"]

    study = tune("xgboost", X, y, group_cv(3), n_trials=2, log=False, storage=storage, max_trees=10)
    assert study.direction == optuna.study.StudyDirection.MINIMIZE
    assert len(study.trials) == 2
    assert study.user_attrs["start_mae"] > 0
    assert all(t.value > 0 for t in study.trials)  # MAE en positivo

    again = tune("xgboost", X, y, group_cv(3), n_trials=3, log=False, storage=storage, max_trees=10)
    assert len(again.trials) == 3  # solo se agregó el que faltaba


def test_tune_requires_group_column():
    X, y = feature_frame(_frame())
    with pytest.raises(ValueError, match=GROUP_COL):
        tune("xgboost", X.drop(columns=[GROUP_COL]), y, group_cv(3), n_trials=1, log=False, max_trees=10)


def test_reserve_groups_disjoint():
    df = _frame(n_schools=40, per_school=5)
    search, reserved = reserve_groups(df)
    assert set(search[GROUP_COL]).isdisjoint(set(reserved[GROUP_COL]))
    assert len(search) + len(reserved) == len(df)
    assert reserved[GROUP_COL].nunique() == 10  # 25 % de 40 sedes


def test_bootstrap_difference_point_value():
    rng = np.random.default_rng(1)
    y = rng.normal(250, 40, 200)
    a, b = y + rng.normal(0, 10, 200), y + rng.normal(0, 20, 200)
    groups = np.repeat(np.arange(20), 10)
    diff, low, high = bootstrap_mae_difference(y, a, b, groups, n_boot=200)
    assert diff == pytest.approx(mean_absolute_error(y, a) - mean_absolute_error(y, b))
    assert low <= diff <= high
    assert bootstrap_mae_difference(y, a, a, groups, n_boot=50) == (0.0, 0.0, 0.0)


def test_bootstrap_resamples_whole_sedes():
    rng = np.random.default_rng(2)
    y = np.full(100, 250.0)
    a = y + rng.normal(0, 30, 100)  # errores distintos fila a fila
    b = y.copy()
    one_school = np.zeros(100)
    # una sola sede: al remuestrear sedes siempre sale la misma → intervalo sin ancho (por filas sí tendría ancho)
    diff, low, high = bootstrap_mae_difference(y, a, b, one_school, n_boot=200)
    assert low == pytest.approx(diff) and high == pytest.approx(diff)
    value, low, high = bootstrap_metric_ci(y, a, one_school, n_boot=50)
    assert low == pytest.approx(value) and high == pytest.approx(value)
    # muchas sedes con errores distintos: el intervalo sí tiene ancho
    many = np.repeat(np.arange(20), 5)
    _, low, high = bootstrap_mae_difference(y, a, b, many, n_boot=200)
    assert high > low


def test_bootstrap_keeps_school_rows_together():
    """Con sedes de distinto tamaño, el intervalo pondera por estudiantes (suma ÷ conteo), no por sede."""
    y = np.zeros(11)
    a = np.array([10.0] * 10 + [0.0])  # sede grande con error 10, sede de 1 estudiante sin error
    b = np.zeros(11)
    groups = np.array([0] * 10 + [1])
    diff, low, high = bootstrap_mae_difference(y, a, b, groups, n_boot=500)
    assert diff == pytest.approx(100 / 11)
    assert low == pytest.approx(0.0) and high == pytest.approx(10.0)  # solo sede 1 / solo sede 0
