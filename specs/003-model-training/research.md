# Research: train.py (regresión)

## 1. Qué se toma del ejemplo y qué no

| Del ejemplo (`creditsight/models/train.py`) | Aquí |
|---|---|
| `candidates()` con (modelo, ¿escalar?) | Igual, con regresores |
| `build_pipeline(model, scale, ...)` | Igual; `scale=True` por defecto porque los notebooks llaman `build_pipeline(modelo)` (escalar no afecta a los árboles) |
| `evaluate_folds` / `evaluate` por grupo | Igual, por `cole_cod_dane_sede` |
| `feature_frame(df)` | Igual; devuelve también `y` |
| `encode_target`, `expected_cost`, `decide_min_cost`, `metrics_from_proba`, `COST_MATRIX` | **No**: son de clasificación con costos distintos; aquí los dos errores cuestan lo mismo (MAE) |
| `use_credit_mix` | **No**: es una columna de crédito |

## 2. Candidatos (parámetros de partida, semilla 42)

| Nombre | Modelo | ¿Escalar? | Motivo |
|---|---|---|---|
| `línea base (mediana)` | `DummyRegressor(strategy="median")` | no | Es la línea base del caso (MAE 42,8): el torneo debe superarla |
| `ridge` | `Ridge(alpha=1.0)` | sí | Modelo lineal simple e interpretable |
| `random forest` | `RandomForestRegressor(n_estimators=200, min_samples_leaf=3, n_jobs=2)` | no | Mismos parámetros que el ejemplo |
| `lightgbm` | `LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=31, n_jobs=2, verbose=-1)` | no | Mismos parámetros que el ejemplo |
| `xgboost` | `XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, tree_method="hist", n_jobs=2)` | no | Mismos parámetros que el ejemplo |

- **Aprobado por el grupo (31 oct 2026):** los 5 candidatos con estos parámetros de partida. En el torneo, LightGBM y
  XGBoost se comparan con su pérdida por defecto; entrenarlos con error absoluto (`objective="l1"` /
  `"reg:absoluteerror"`) queda para la etapa 6.

## 3. Métricas

**Decisión del grupo (31 oct 2026):** el MAE y el RMSE se reportan en positivo, con una prueba que lo verifique.

**Riesgo detectado y diseño propuesto (pendiente de confirmar por el grupo):** si `scoring()` entregara scorers con el MAE
positivo, `cross_validate` lo mostraría bien, pero `GridSearchCV`, Optuna y el `refit` del notebook 06 **maximizan** el
puntaje y elegirían el modelo que más se equivoca. Por eso:

- `scoring()` = `{"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}` (negativos: así los
  usan la validación cruzada y la búsqueda de la etapa 6).
- `cv_report(cv_results)` convierte la salida de `cross_validate` en una tabla con **MAE y RMSE positivos** (cambia el
  signo) y R² igual; es lo que se muestra y se anota en `reports/`.
- `regression_metrics(y_true, y_pred)` devuelve MAE, RMSE y R² directamente en positivo.
- `evaluate_folds` / `evaluate` usan `regression_metrics`: también positivos.

**Alternative considered**: scorers positivos con `make_scorer(mean_absolute_error, greater_is_better=True)` (rechazada:
invierte la búsqueda de la etapa 6).

## 4. LightGBM en Windows

- **Hallazgo (31 oct 2026)**: `import lightgbm` falla en el `.venv`: falta `vcomp140.dll` (OpenMP de Microsoft), que viene
  en el **Microsoft Visual C++ Redistributable (x64)**. `lib_lightgbm.dll` sí está. XGBoost 3.4.1 carga bien.
- **Decision (grupo, 31 oct 2026)**: LightGBM se queda en el torneo; el grupo instala el redistribuible (tarea T001).
  `train.py` importa LightGBM normalmente: si falta, el error debe verse, no esconderse ni omitirse.
- **Alternative considered**: importar LightGBM solo si está disponible y omitirlo en silencio (rechazado: el torneo
  cambiaría sin que nadie lo note).

## 5. Dependencia con la etapa 3

`evaluate_folds` usa `GROUP_COL` de `src/proyecto/data/split.py`. La etapa 3 (plan pendiente de aprobación) se implementa
antes que esta pieza.
