# Contrato: `src/proyecto/models/train.py`

| Función | Firma | Devuelve |
|---|---|---|
| `candidates` | `candidates(random_state: int = 42) -> dict[str, tuple[estimator, bool]]` | nombre → (modelo sin ajustar, ¿escalar?) |
| `build_pipeline` | `build_pipeline(model, scale=True, use_engineered=False, extra_numeric=None, min_frequency=0.01) -> Pipeline` | pasos `features` (solo si `use_engineered`, `FunctionTransformer(add_features)`), `prep` (`build_preprocessor`), `model` |
| `scoring` | `scoring() -> dict[str, str]` | `{"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}` (negativos a propósito: la búsqueda de la etapa 6 maximiza) |
| `cv_report` | `cv_report(cv_results: dict) -> pd.DataFrame` | una fila por pliegue con `mae` y `rmse` **positivos** y `r2`, a partir de la salida de `cross_validate(..., scoring=scoring())` |
| `regression_metrics` | `regression_metrics(y_true, y_pred) -> dict[str, float]` | `{"mae", "rmse", "r2"}` positivos |
| `evaluate_folds` | `evaluate_folds(pipeline, X, y, cv) -> pd.DataFrame` | una fila por pliegue: `mae`, `rmse`, `r2`, `fit_seconds`; grupos = `X[GROUP_COL]`; `ValueError` si falta `GROUP_COL` |
| `evaluate` | `evaluate(pipeline, X, y, cv) -> dict` | `<métrica>_mean`, `<métrica>_std`, `fit_seconds`; `ValueError` si falta `GROUP_COL` |
| `feature_frame` | `feature_frame(df) -> tuple[pd.DataFrame, pd.Series]` | `X` sin `punt_global` (con `cole_cod_dane_sede`), `y = punt_global` |

Constante: `TARGET = "punt_global"`. `GROUP_COL` se importa de `proyecto.data.split`.
