"""Candidatos, pipeline del modelo y métricas de regresión con validación agrupada por sede.

Adaptado del `train.py` del ejemplo (CreditSight), que es de clasificación con matriz de costos. Aquí es regresión: los
dos errores cuestan lo mismo, así que la métrica principal es el MAE (en puntos) y no hay regla de decisión. LightGBM se
reemplazó por HistGradientBoostingRegressor de scikit-learn (decisión del grupo, 31 oct 2026: LightGBM no carga en
Windows sin el Visual C++ Redistributable). Motivos en `specs/003-model-training/research.md`.
"""
import time

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from xgboost import XGBRegressor

from proyecto.data.split import GROUP_COL, RANDOM_STATE
from proyecto.features.engineering import add_features, build_preprocessor

TARGET = "punt_global"


def candidates(random_state: int = RANDOM_STATE) -> dict:
    """Modelos del torneo; el booleano indica si necesitan variables escaladas. Parámetros de partida del ejemplo."""
    return {
        "línea base (mediana)": (DummyRegressor(strategy="median"), False),
        "ridge": (Ridge(alpha=1.0), True),
        "random forest": (
            RandomForestRegressor(n_estimators=200, min_samples_leaf=3, n_jobs=2, random_state=random_state),
            False,
        ),
        # Equivalente a LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=31) del ejemplo; sin parada
        # temprana, que scikit-learn activaría sola con más de 10.000 filas.
        "hist gradient boosting": (
            HistGradientBoostingRegressor(
                max_iter=300, learning_rate=0.05, max_leaf_nodes=31, early_stopping=False, random_state=random_state
            ),
            False,
        ),
        "xgboost": (
            XGBRegressor(
                n_estimators=300, learning_rate=0.05, max_depth=6, tree_method="hist",
                random_state=random_state, n_jobs=2,
            ),
            False,
        ),
    }


def build_pipeline(
    model,
    scale: bool = True,
    use_engineered: bool = False,
    extra_numeric: list[str] | None = None,
    min_frequency: float | None = 0.01,
) -> Pipeline:
    """Pipeline completo: (variables nuevas) -> preprocesamiento -> modelo. Se guarda entero.

    `scale=True` por defecto porque los notebooks llaman `build_pipeline(modelo)`; escalar no cambia a los árboles.
    """
    steps = []
    if use_engineered:
        steps.append(("features", FunctionTransformer(add_features)))
    steps.append(
        (
            "prep",
            build_preprocessor(
                scale=scale, use_engineered=use_engineered, extra_numeric=extra_numeric, min_frequency=min_frequency
            ),
        )
    )
    steps.append(("model", model))
    return Pipeline(steps)


def scoring() -> dict:
    """Métricas para `cross_validate`. MAE y RMSE salen negativos a propósito: la búsqueda de la etapa 6 maximiza.

    Para leerlos en positivo, usar `cv_report`.
    """
    return {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}


def cv_report(cv_results: dict) -> pd.DataFrame:
    """Salida de `cross_validate(..., scoring=scoring())` -> una fila por pliegue con MAE y RMSE en positivo."""
    return pd.DataFrame({
        "mae": -np.asarray(cv_results["test_mae"]),
        "rmse": -np.asarray(cv_results["test_rmse"]),
        "r2": np.asarray(cv_results["test_r2"]),
    }).rename_axis("fold")


def regression_metrics(y_true, y_pred) -> dict:
    """MAE (métrica principal), RMSE (revela errores grandes) y R², en puntos y en positivo."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(root_mean_squared_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def _require_group_col(X: pd.DataFrame) -> None:
    """Sin la sede no se puede validar agrupado; mejor un error claro que una validación por fila sin avisar."""
    if GROUP_COL not in X.columns:
        raise ValueError(f"Falta la columna de agrupación '{GROUP_COL}': la validación debe agruparse por sede.")


def evaluate_folds(pipeline, X: pd.DataFrame, y: pd.Series, cv) -> pd.DataFrame:
    """Validación cruzada por sede. Una fila por pliegue con las métricas y el tiempo de ajuste."""
    _require_group_col(X)
    y = pd.Series(y).reset_index(drop=True)
    X = X.reset_index(drop=True)
    rows = []
    for fold, (train_idx, valid_idx) in enumerate(cv.split(X, y, groups=X[GROUP_COL])):
        model = clone(pipeline)
        start = time.time()
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        seconds = time.time() - start
        metrics = regression_metrics(y.iloc[valid_idx], model.predict(X.iloc[valid_idx]))
        rows.append({"fold": fold, **metrics, "fit_seconds": seconds})
    return pd.DataFrame(rows).set_index("fold")


def evaluate(pipeline, X: pd.DataFrame, y: pd.Series, cv) -> dict:
    """Como `evaluate_folds`, pero devuelve la media y la desviación entre pliegues de cada métrica."""
    table = evaluate_folds(pipeline, X, y, cv)
    out = {f"{name}_mean": float(table[name].mean()) for name in table if name != "fit_seconds"}
    out.update({f"{name}_std": float(table[name].std()) for name in table if name != "fit_seconds"})
    out["fit_seconds"] = float(table["fit_seconds"].mean())
    return out


def feature_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa X (sin el objetivo; conserva la sede para agrupar, el preprocesamiento la ignora) e y."""
    return df.drop(columns=[TARGET]), df[TARGET]
