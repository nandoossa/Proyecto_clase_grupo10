"""Pruebas de train.py: pipeline del modelo, candidatos y métricas (regresión con MAE).

Las tablas se arman a mano con valores inventados y modelos pequeños, para que las pruebas corran rápido.
"""
import numpy as np
import pytest
from sklearn.base import is_regressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, cross_validate

from proyecto.data.split import GROUP_COL
from proyecto.models.train import (
    TARGET,
    build_pipeline,
    candidates,
    cv_report,
    evaluate,
    evaluate_folds,
    feature_frame,
    regression_metrics,
    scoring,
)


class _RecordingGroupKFold(GroupKFold):
    """GroupKFold que guarda los grupos que recibió, para comprobar que evaluate_folds agrupa por sede."""

    def split(self, X, y=None, groups=None):
        self.seen_groups = groups
        return super().split(X, y, groups)


# --- Historia 1: pipeline ---


def test_build_pipeline_steps():
    assert [name for name, _ in build_pipeline(Ridge()).steps] == ["prep", "model"]
    assert [name for name, _ in build_pipeline(Ridge(), use_engineered=True).steps] == ["features", "prep", "model"]


def test_pipeline_fits_and_predicts_without_nan(school_frame):
    X, y = feature_frame(school_frame())
    for model in (DummyRegressor(strategy="median"), Ridge()):
        pred = build_pipeline(model).fit(X, y).predict(X)
        assert pred.shape == (len(X),) and not np.isnan(pred).any()


def test_pipeline_ignores_school_id_and_target(school_frame):
    X, y = feature_frame(school_frame())
    assert TARGET not in X.columns and GROUP_COL in X.columns
    pipeline = build_pipeline(Ridge()).fit(X, y)
    shuffled = X.assign(**{GROUP_COL: X[GROUP_COL].to_numpy()[::-1]})
    np.testing.assert_allclose(pipeline.predict(X), pipeline.predict(shuffled))


# --- Historia 2: candidatos y métricas ---


def test_candidates_are_regressors_with_baseline():
    models = candidates()
    assert list(models) == ["línea base (mediana)", "ridge", "random forest", "hist gradient boosting", "xgboost"]
    assert all(is_regressor(model) for model, _ in models.values())
    baseline, _ = models["línea base (mediana)"]
    assert isinstance(baseline, DummyRegressor) and baseline.strategy == "median"
    assert [name for name, (_, scale) in models.items() if scale] == ["ridge"]
    hgb, _ = models["hist gradient boosting"]
    assert isinstance(hgb, HistGradientBoostingRegressor)
    assert (hgb.max_iter, hgb.learning_rate, hgb.max_leaf_nodes, hgb.early_stopping) == (300, 0.05, 31, False)


def test_regression_metrics_known_values():
    perfect = regression_metrics([100, 200, 300], [100, 200, 300])
    assert perfect == {"mae": 0.0, "rmse": 0.0, "r2": 1.0}
    result = regression_metrics([100, 200], [110, 190])
    assert result["mae"] == pytest.approx(10) and result["rmse"] == pytest.approx(10)


def test_mae_and_rmse_are_reported_positive(school_frame):
    X, y = feature_frame(school_frame())
    folds = list(GroupKFold(5).split(X, y, groups=X[GROUP_COL]))
    assert set(scoring()) == {"mae", "rmse", "r2"}
    raw = cross_validate(build_pipeline(Ridge()), X, y, cv=folds, scoring=scoring())
    assert (raw["test_mae"] <= 0).all()  # scikit-learn los da en negativo...
    report = cv_report(raw)
    assert (report["mae"] >= 0).all() and (report["rmse"] >= 0).all()  # ...y aquí se reportan en positivo

    for i, (train_idx, valid_idx) in enumerate(folds):
        model = build_pipeline(Ridge()).fit(X.iloc[train_idx], y.iloc[train_idx])
        expected = regression_metrics(y.iloc[valid_idx], model.predict(X.iloc[valid_idx]))
        assert report["mae"].iloc[i] == pytest.approx(expected["mae"])
        assert report["rmse"].iloc[i] == pytest.approx(expected["rmse"])

    table = evaluate_folds(build_pipeline(Ridge()), X, y, GroupKFold(5))
    assert (table["mae"] >= 0).all() and (table["rmse"] >= 0).all()


def test_evaluate_folds_groups_by_school(school_frame):
    X, y = feature_frame(school_frame())
    cv = _RecordingGroupKFold(5)
    table = evaluate_folds(build_pipeline(Ridge()), X, y, cv)
    assert len(table) == 5 and {"mae", "rmse", "r2", "fit_seconds"} <= set(table.columns)
    assert cv.seen_groups.equals(X[GROUP_COL])
    for train_idx, valid_idx in cv.split(X, y, groups=X[GROUP_COL]):
        assert set(X[GROUP_COL].iloc[train_idx]).isdisjoint(X[GROUP_COL].iloc[valid_idx])


def test_baseline_mae_is_median_rule(school_frame):
    X, y = feature_frame(school_frame())
    cv = GroupKFold(5)
    table = evaluate_folds(build_pipeline(DummyRegressor(strategy="median")), X, y, cv)
    for i, (train_idx, valid_idx) in enumerate(cv.split(X, y, groups=X[GROUP_COL])):
        by_hand = np.mean(np.abs(y.iloc[valid_idx] - y.iloc[train_idx].median()))
        assert table["mae"].iloc[i] == pytest.approx(by_hand)


def test_evaluate_returns_mean_and_std(school_frame):
    X, y = feature_frame(school_frame())
    result = evaluate(build_pipeline(Ridge()), X, y, GroupKFold(5))
    assert {"mae_mean", "mae_std", "rmse_mean", "r2_mean", "fit_seconds"} <= set(result)


def test_evaluate_requires_group_column(school_frame):
    X, y = feature_frame(school_frame())
    X = X.drop(columns=[GROUP_COL])
    with pytest.raises(ValueError):
        evaluate_folds(build_pipeline(Ridge()), X, y, GroupKFold(5))
    with pytest.raises(ValueError):
        evaluate(build_pipeline(Ridge()), X, y, GroupKFold(5))
