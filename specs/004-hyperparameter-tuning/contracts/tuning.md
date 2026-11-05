# Contrato: `src/proyecto/models/tuning.py`

| Función / constante | Firma | Devuelve |
|---|---|---|
| `hgb_space` | `hgb_space(trial) -> dict` | `min_frequency`, `loss`, `learning_rate`, `max_iter`, `max_leaf_nodes`, `min_samples_leaf`, `l2_regularization`, `max_features` (rangos de `especificaciones/06-optimizacion.md` §4) |
| `xgb_space` | `xgb_space(trial) -> dict` | `min_frequency`, `objective`, `learning_rate`, `n_estimators`, `max_depth`, `min_child_weight`, `subsample`, `colsample_bytree`, `reg_lambda` |
| `make_hgb` | `make_hgb(params, random_state=42) -> HistGradientBoostingRegressor` | modelo con `early_stopping=False`; ignora `min_frequency` (va al preprocesador) |
| `make_xgb` | `make_xgb(params, random_state=42) -> XGBRegressor` | modelo con `tree_method="hist"`, `n_jobs=2`; ignora `min_frequency` |
| `STARTING_PARAMS` | `dict[str, dict]` | parámetros de partida del torneo por modelo, en el formato de los espacios (`min_frequency=0.01`, pérdida cuadrática) |
| `MODELS` | `dict[str, tuple[space_fn, make_fn]]` | `"hist gradient boosting"` y `"xgboost"` (mismos nombres que `candidates()`) |
| `build_tuned_pipeline` | `build_tuned_pipeline(name, params) -> Pipeline` | `build_pipeline(make_fn(params), scale=False, min_frequency=params["min_frequency"])` |
| `reserve_groups` | `reserve_groups(df, frac=0.25, seed=7) -> (search, reserved)` | sin sedes en común (usa `split_by_group`) |
| `tune` | `tune(name, X, y, cv, n_trials, seed=42, log=True, storage=None, max_trees=None) -> optuna.Study` | estudio que minimiza el MAE; `study.user_attrs["start_mae"]` con el MAE de partida en los mismos pliegues; reanuda si `storage` ya tiene ensayos (si ya está completo, no abre otra ejecución en MLflow); `max_trees` limita los árboles, solo para pruebas; `study.user_attrs`: `start_*`, `search_seconds`, `mlflow_parent_run_id` |
| `bootstrap_mae_difference` | `bootstrap_mae_difference(y_true, pred_a, pred_b, groups, n_boot=1000, seed=42) -> (diff, low, high)` | MAE(A) − MAE(B) e intervalo 95 % remuestreando sedes; negativo: A se equivoca menos |
| `bootstrap_metric_ci` | `bootstrap_metric_ci(y_true, pred, groups, metric_fn=mean_absolute_error, n_boot=1000, seed=42) -> (value, low, high)` | métrica e intervalo 95 % remuestreando sedes |

Etiquetas MLflow de cada ensayo: `etapa=06_optimizacion`, `modelo=<nombre>`, `metrica_optimizada=mae`. Métricas: `mae`,
`rmse`, `r2`, `mae_std`, `rmse_std`, `r2_std`, `fit_seconds`.
