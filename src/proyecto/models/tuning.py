"""Optimización de hiperparámetros de los finalistas con Optuna, registrando cada ensayo en MLflow.

Adaptado del `tuning.py` del ejemplo (CreditSight), que es de clasificación con matriz de costos. Aquí es regresión:
- se minimiza el **MAE** medio entre pliegues agrupados por sede (y se registran RMSE y R² con su desviación);
- no hay probabilidades, AUC, F1, costos ni regla de decisión;
- los finalistas son HistGradientBoosting (en lugar de LightGBM, que no carga en los equipos del grupo) y XGBoost;
- el umbral de poco frecuentes (`min_frequency`) y la función de pérdida entran en la búsqueda (pendientes de las etapas
  4 y 5);
- el bootstrap remuestrea **sedes** completas, no filas, y compara diferencias de MAE.
Reglas y rangos en `especificaciones/06-optimizacion.md`; contrato en `specs/004-hyperparameter-tuning/contracts/tuning.md`.
"""
import time
from pathlib import Path

import mlflow
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from proyecto.data.split import RANDOM_STATE, split_by_group
from proyecto.models.train import build_pipeline, evaluate_folds
from proyecto.tracking.mlflow_utils import log_run

STAGE_TAG = "06_optimizacion"
METRIC = "mae"  # métrica que se optimiza (dirección: minimizar)


def hgb_space(trial: optuna.Trial) -> dict:
    """Espacio de HistGradientBoosting, alrededor de los parámetros de partida del torneo (motivos en la especificación)."""
    return {
        "min_frequency": trial.suggest_categorical("min_frequency", [0.01, 0.001]),
        "loss": trial.suggest_categorical("loss", ["squared_error", "absolute_error"]),
        "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.2, log=True),
        "max_iter": trial.suggest_int("max_iter", 150, 600),
        "max_leaf_nodes": trial.suggest_int("max_leaf_nodes", 15, 63),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 20, 200),
        "l2_regularization": trial.suggest_float("l2_regularization", 1e-3, 10.0, log=True),
        "max_features": trial.suggest_float("max_features", 0.5, 1.0),
    }


def xgb_space(trial: optuna.Trial) -> dict:
    """Espacio de XGBoost, alrededor de los parámetros de partida del torneo (motivos en la especificación)."""
    return {
        "min_frequency": trial.suggest_categorical("min_frequency", [0.01, 0.001]),
        "objective": trial.suggest_categorical("objective", ["reg:squarederror", "reg:absoluteerror"]),
        "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.2, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 150, 600),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "min_child_weight": trial.suggest_float("min_child_weight", 1.0, 100.0, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }


def _model_params(params: dict) -> dict:
    """`min_frequency` es del preprocesador, no del modelo."""
    return {k: v for k, v in params.items() if k != "min_frequency"}


def make_hgb(params: dict, random_state: int = RANDOM_STATE) -> HistGradientBoostingRegressor:
    # Sin parada temprana, como en el torneo (scikit-learn la activaría sola con más de 10.000 filas).
    return HistGradientBoostingRegressor(early_stopping=False, random_state=random_state, **_model_params(params))


def make_xgb(params: dict, random_state: int = RANDOM_STATE) -> XGBRegressor:
    return XGBRegressor(tree_method="hist", n_jobs=2, random_state=random_state, **_model_params(params))


# Parámetros de partida del torneo (`candidates()` de train.py), con el umbral de la etapa 4 y la pérdida por defecto.
# Lo que no aparece queda en el valor por defecto de la librería, igual que en el torneo.
STARTING_PARAMS = {
    "hist gradient boosting": {
        "min_frequency": 0.01, "loss": "squared_error", "learning_rate": 0.05, "max_iter": 300, "max_leaf_nodes": 31,
    },
    "xgboost": {
        "min_frequency": 0.01, "objective": "reg:squarederror", "learning_rate": 0.05, "n_estimators": 300,
        "max_depth": 6,
    },
}

# Mismos nombres que `candidates()`: (espacio de búsqueda, fábrica del modelo). Ninguno necesita escalado (árboles).
MODELS = {
    "hist gradient boosting": (hgb_space, make_hgb),
    "xgboost": (xgb_space, make_xgb),
}
_TREES_PARAM = {"hist gradient boosting": "max_iter", "xgboost": "n_estimators"}


def build_tuned_pipeline(name: str, params: dict) -> Pipeline:
    """Preprocesamiento de la etapa 4 (con el `min_frequency` del ensayo) + modelo con esos parámetros."""
    _, make_fn = MODELS[name]
    return build_pipeline(make_fn(params), scale=False, min_frequency=params["min_frequency"])


def reserve_groups(df: pd.DataFrame, frac: float = 0.25, seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa dentro del entrenamiento una fracción de **sedes** que la búsqueda nunca ve. Devuelve (búsqueda, reserva).

    Usa `split_by_group`, que verifica que ninguna sede quede en los dos lados.
    """
    return split_by_group(df, test_size=frac, seed=seed)


def _summary(folds: pd.DataFrame) -> dict:
    """Tabla por pliegue -> media de cada métrica, su desviación entre pliegues y el tiempo medio de ajuste."""
    out = {col: float(folds[col].mean()) for col in ["mae", "rmse", "r2", "fit_seconds"]}
    out.update({f"{col}_std": float(folds[col].std()) for col in ["mae", "rmse", "r2"]})
    return out


def _cap_trees(name: str, params: dict, max_trees: int | None) -> dict:
    """Solo para pruebas: limita el número de árboles para que corran en segundos."""
    if max_trees is None:
        return params
    key = _TREES_PARAM[name]
    return {**params, key: min(params.get(key, max_trees), max_trees)}


def tune(name: str, X: pd.DataFrame, y, cv, n_trials: int, seed: int = RANDOM_STATE, log: bool = True,
         storage: str | Path | None = None, max_trees: int | None = None) -> optuna.Study:
    """Estudio de Optuna que **minimiza el MAE** medio entre pliegues agrupados por sede.

    Antes de buscar, mide los parámetros de partida del torneo con los mismos pliegues (`study.user_attrs["start_mae"]`,
    ejecución `<modelo>-partida`): es el «antes» comparable. Cada ensayo queda como ejecución anidada en MLflow con MAE,
    RMSE y R² (media y desviación entre pliegues) y el tiempo de ajuste.

    Con `storage` (ruta de un archivo .db) el estudio se guarda en disco y **se reanuda**: si la ejecución se corta, al volver
    a llamar solo se hacen los ensayos que faltan hasta completar `n_trials`. `max_trees` es solo para pruebas.
    """
    space_fn, _ = MODELS[name]
    tags = {"etapa": STAGE_TAG, "modelo": name, "metrica_optimizada": METRIC}

    def objective(trial: optuna.Trial) -> float:
        params = _cap_trees(name, space_fn(trial), max_trees)
        folds = evaluate_folds(build_tuned_pipeline(name, params), X, y, cv)
        board = _summary(folds)
        for key in ["mae_std", "rmse", "rmse_std", "r2", "r2_std", "fit_seconds"]:
            trial.set_user_attr(key, board[key])
        if log:
            log_run(f"{name}-ensayo-{trial.number:02d}", params, board, tags=tags, nested=True)
        return board["mae"]

    def measure_start() -> None:
        """Parámetros del torneo, mismos pliegues y mismos datos que los ensayos."""
        if "start_mae" in study.user_attrs:
            return
        params = _cap_trees(name, STARTING_PARAMS[name], max_trees)
        board = _summary(evaluate_folds(build_tuned_pipeline(name, params), X, y, cv))
        for key, value in board.items():
            study.set_user_attr(f"start_{key}", value)
        if log:
            log_run(f"{name}-partida", params, board, tags={**tags, "tipo": "partida"}, nested=True)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=seed),
        study_name=f"saber11-{name.replace(' ', '-')}-{METRIC}",
        storage=(f"sqlite:///{Path(storage).as_posix()}" if storage else None),
        load_if_exists=True,
    )
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    done = len([t for t in study.trials if t.state.is_finished()])
    remaining = max(n_trials - done, 0)
    if done:
        print(f"  {name}: se reanuda el estudio ({done} ensayos ya hechos, faltan {remaining})")
    if remaining == 0 and "start_mae" in study.user_attrs:
        return study  # ya completo: no se abre otra ejecución madre vacía en MLflow

    start = time.time()
    # Un ensayo con una combinación que falla (ValueError) queda como fallido y la búsqueda sigue.
    if log:
        with mlflow.start_run(run_name=f"optuna-{name}") as parent:
            mlflow.set_tags(tags)
            measure_start()
            study.optimize(objective, n_trials=remaining, catch=(ValueError,))
            mlflow.log_metric(f"best_{METRIC}", study.best_value)
            mlflow.log_metric(f"start_{METRIC}", study.user_attrs["start_mae"])
            mlflow.log_params({f"best_{k}": v for k, v in study.best_params.items()})
            study.set_user_attr("mlflow_parent_run_id", parent.info.run_id)
    else:
        measure_start()
        study.optimize(objective, n_trials=remaining, catch=(ValueError,))
    study.set_user_attr("search_seconds", study.user_attrs.get("search_seconds", 0.0) + time.time() - start)
    return study


def bootstrap_mae_difference(y_true, pred_a, pred_b, groups, n_boot: int = 1000, seed: int = RANDOM_STATE):
    """MAE(A) − MAE(B) con intervalo del 95 %, remuestreando **sedes** completas.

    Remuestrear filas sería otra fuga: los estudiantes de una misma sede no son independientes. Cada remuestreo toma sedes
    con reemplazo y calcula (suma de |error A| − |error B| de esas sedes) ÷ (estudiantes de esas sedes).
    Negativo: A se equivoca menos que B. Devuelve (diferencia, límite inferior, límite superior).
    """
    y_true = np.asarray(y_true, dtype=float)
    diff = np.abs(y_true - np.asarray(pred_a)) - np.abs(y_true - np.asarray(pred_b))
    per_school = pd.DataFrame({"g": np.asarray(groups), "d": diff}).groupby("g")["d"].agg(["sum", "count"])
    sums, counts = per_school["sum"].to_numpy(), per_school["count"].to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sums), size=(n_boot, len(sums)))
    boot = sums[idx].sum(axis=1) / counts[idx].sum(axis=1)
    return float(sums.sum() / counts.sum()), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def bootstrap_metric_ci(y_true, pred, groups, metric_fn=mean_absolute_error, n_boot: int = 1000,
                        seed: int = RANDOM_STATE):
    """Una métrica (por defecto el MAE) con su intervalo del 95 %, remuestreando **sedes** completas (no filas).

    `metric_fn(y_true, pred)` devuelve un número. Devuelve (valor, límite inferior, límite superior).
    """
    y_true, pred, groups = np.asarray(y_true, dtype=float), np.asarray(pred, dtype=float), np.asarray(groups)
    rows_by_school = list(pd.Series(np.arange(len(groups))).groupby(groups).apply(lambda s: s.to_numpy()))
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(n_boot):
        picked = rng.integers(0, len(rows_by_school), len(rows_by_school))
        rows = np.concatenate([rows_by_school[i] for i in picked])
        values.append(metric_fn(y_true[rows], pred[rows]))
    return float(metric_fn(y_true, pred)), float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))
