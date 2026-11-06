"""Validación final (etapa 7): equidad por segmento, diferencias de métricas por sede e importancia por permutación.

Este módulo **no abre la prueba**: recibe las predicciones que le pasa el notebook 07, que abre `test.joblib` una sola vez.
Todos los intervalos remuestrean **sedes** completas (los estudiantes de una sede no son independientes).
Reglas en `especificaciones/07-validacion.md`; contrato en `specs/005-validation/contracts/evaluation.md`.
"""
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

from proyecto.data.split import RANDOM_STATE
from proyecto.features.engineering import feature_columns
from proyecto.models.tuning import bootstrap_mae_difference

MISSING_LABEL = "Sin dato (vacío)"
CLEAR = "cumple con ventaja clara"
INCONCLUSIVE = "cumple sin ventaja concluyente"
FAILS = "no cumple"


def stratum_segment(df: pd.DataFrame) -> pd.Series:
    """Estrato como segmento: «Estrato 1» … «Estrato 6», «Sin Estrato» (marca `sin_estrato` = 1) o «Sin dato (vacío)».

    «Sin Estrato» llega como vacío en `fami_estratovivienda` con `sin_estrato` = 1 (regla 7b de la etapa 3); un vacío real
    tiene `sin_estrato` = 0. Ningún vacío se convierte en estrato 0.
    """
    stratum = df["fami_estratovivienda"]
    labels = "Estrato " + stratum.astype("Int64").astype(str)
    labels = labels.where(stratum.notna(), MISSING_LABEL)
    return labels.where(~(stratum.isna() & (df["sin_estrato"] == 1)), "Sin Estrato").rename("estrato")


def equity_segments(df: pd.DataFrame) -> pd.DataFrame:
    """Segmentos de la condición de equidad: estrato, zona, naturaleza del colegio y género. Vacío → «Sin dato (vacío)»."""
    return pd.DataFrame({
        "estrato": stratum_segment(df),
        "zona": df["cole_area_ubicacion"].fillna(MISSING_LABEL),
        "naturaleza": df["cole_naturaleza"].fillna(MISSING_LABEL),
        "genero": df["estu_genero"].fillna(MISSING_LABEL),
    }, index=df.index)


def bootstrap_metric_difference(y_true, pred_a, pred_b, groups, metric_fn, n_boot: int = 1000, seed: int = RANDOM_STATE):
    """métrica(A) − métrica(B) con intervalo del 95 %, remuestreando **sedes** completas.

    En cada remuestreo se usan las mismas sedes para A y para B (comparación pareada). Sirve para RMSE y R², que no se
    pueden promediar por fila como el MAE. Devuelve (diferencia, límite inferior, límite superior).
    """
    y_true, pred_a, pred_b = (np.asarray(v, dtype=float) for v in (y_true, pred_a, pred_b))
    groups = np.asarray(groups)
    rows_by_school = list(pd.Series(np.arange(len(groups))).groupby(groups).apply(lambda s: s.to_numpy()))
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        picked = rng.integers(0, len(rows_by_school), len(rows_by_school))
        rows = np.concatenate([rows_by_school[i] for i in picked])
        diffs.append(metric_fn(y_true[rows], pred_a[rows]) - metric_fn(y_true[rows], pred_b[rows]))
    full = metric_fn(y_true, pred_a) - metric_fn(y_true, pred_b)
    return float(full), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def equity_table(y_true, pred_model, pred_base, segments: pd.DataFrame, groups, n_boot: int = 1000,
                 seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Una fila por (variable, segmento) con estudiantes, sedes, MAE del modelo y de la línea base y el veredicto.

    Regla (escrita antes de abrir la prueba): **cumple** si el MAE del modelo es estrictamente menor que el de la línea base.
    Los que cumplen se clasifican con el intervalo del 95 % (por sedes) de la diferencia modelo − línea base: «con ventaja
    clara» si el intervalo excluye el cero, «sin ventaja concluyente» si lo incluye.
    """
    y_true, pred_model, pred_base = (np.asarray(v, dtype=float) for v in (y_true, pred_model, pred_base))
    groups = np.asarray(groups)
    rows = []
    for variable in segments.columns:
        values = segments[variable].to_numpy()
        for segment in sorted(pd.unique(values)):
            mask = values == segment
            mae_model = float(np.mean(np.abs(y_true[mask] - pred_model[mask])))
            mae_base = float(np.mean(np.abs(y_true[mask] - pred_base[mask])))
            diff, low, high = bootstrap_mae_difference(y_true[mask], pred_model[mask], pred_base[mask], groups[mask],
                                                       n_boot=n_boot, seed=seed)
            meets = mae_model < mae_base
            rows.append({
                "variable": variable, "segmento": segment, "estudiantes": int(mask.sum()),
                "sedes": int(pd.unique(groups[mask]).size), "mae_modelo": mae_model, "mae_linea_base": mae_base,
                "diferencia": diff, "ic_inf": low, "ic_sup": high, "cumple": bool(meets),
                "veredicto": (CLEAR if high < 0 else INCONCLUSIVE) if meets else FAILS,
            })
    return pd.DataFrame(rows).set_index(["variable", "segmento"])


def model_columns() -> list[str]:
    """Las columnas originales que usa el preprocesador (sin la sede, que solo sirve para agrupar)."""
    numeric, categorical = feature_columns()
    return numeric + categorical


def permutation_importance_table(pipeline, X: pd.DataFrame, y, columns: list[str], n_repeats: int = 5,
                                 seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Cuánto sube el MAE (en puntos) al desordenar cada columna original. Mayor = el modelo se apoya más en ella.

    Se permutan las columnas **originales** (antes del one-hot), así cada variable cuenta como una sola. Explica al modelo,
    no al mundo: las variables correlacionadas se reparten el crédito y una importancia alta no es causa.
    """
    # H8 (auditoría de la etapa 7): solo se desordenan las columnas que usa el modelo; las demás (por ejemplo, la sede)
    # se quitan antes. No se filtra a `columns`, porque el modelo necesita todas sus columnas para predecir. scikit-learn
    # usa una sola semilla para todas las columnas, así que el resultado es el mismo que pasando X[model_columns()], como
    # hizo el notebook 07.
    X = X[model_columns()]
    result = permutation_importance(pipeline, X, y, scoring="neg_mean_absolute_error", n_repeats=n_repeats,
                                    random_state=seed, n_jobs=1)
    table = pd.DataFrame({"aumento_mae": result.importances_mean, "desviacion": result.importances_std},
                         index=pd.Index(X.columns, name="columna"))
    return table.loc[columns].sort_values("aumento_mae", ascending=False)
