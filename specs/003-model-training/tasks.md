---

description: "Lista de tareas: train.py (pipeline de modelo, candidatos y métricas)"
---

# Tasks: Pipeline de modelo, candidatos y métricas (train.py)

**Input**: Design documents from `/specs/003-model-training/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/train.md; **etapa 3 implementada** (`GROUP_COL` en `split.py`)

**Tests**: se piden (`CLAUDE.md`, regla 9). Cada prueba se escribe antes que su función y debe fallar primero.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [ ] T001 Instalar el Microsoft Visual C++ Redistributable (x64) y comprobar `python -c "import lightgbm"` sin error (lo hace un integrante; requiere permisos de administrador)
- [ ] T002 Crear `src/proyecto/models/train.py` con docstring en español (qué cambia respecto del ejemplo: regresión con MAE, sin matriz de costos) y `TARGET = "punt_global"`; importar `GROUP_COL` de `proyecto.data.split`
- [ ] T003 [P] Crear `tests/test_models.py` con una función `_frame(n_sedes, por_sede)` que arma una tabla hecha a mano con las columnas de la etapa 3 (valores inventados) y un `punt_global` que depende de una o dos columnas

---

## Phase 2: User Story 1 - Unir variables, preprocesamiento y modelo en un Pipeline (P1) 🎯 MVP

### Pruebas (primero; deben fallar)

- [ ] T004 [P] [US1] `test_build_pipeline_steps`: `build_pipeline(Ridge())` tiene pasos `prep` y `model`; con `use_engineered=True` aparece antes `features`
- [ ] T005 [P] [US1] `test_pipeline_fits_and_predicts_without_nan`: `build_pipeline(DummyRegressor(strategy="median"))` y `build_pipeline(Ridge())` se ajustan sobre `X` de `feature_frame` y predicen un número por fila, sin vacíos
- [ ] T006 [P] [US1] `test_pipeline_ignores_school_id_and_target`: cambiar los valores de `cole_cod_dane_sede` no cambia las predicciones; `X` de `feature_frame` no contiene `punt_global`

### Implementación

- [ ] T007 [US1] Implementar `feature_frame(df)` y `build_pipeline(model, scale=True, use_engineered=False, extra_numeric=None, min_frequency=0.01)` en `src/proyecto/models/train.py` (como en `contracts/train.md`)
- [ ] T008 [US1] `PYTHONUTF8=1 python -m pytest tests/test_models.py` → T004–T006 en verde

---

## Phase 3: User Story 2 - Comparar candidatos con la misma vara (P1)

### Pruebas (primero; deben fallar)

- [ ] T009 [P] [US2] `test_candidates_are_regressors_with_baseline`: `candidates()` tiene los 5 nombres de `research.md` §2, todos son regresores (`is_regressor`), la línea base es `DummyRegressor(strategy="median")` y solo `ridge` pide escalado
- [ ] T010 [P] [US2] `test_regression_metrics_known_values`: predicciones perfectas → MAE 0, RMSE 0, R² 1; `y=[100, 200]`, `pred=[110, 190]` → MAE 10, RMSE 10
- [ ] T011 [P] [US2] `test_mae_and_rmse_are_reported_positive`: `scoring()` tiene `mae`, `rmse`, `r2`; tras `cross_validate(..., scoring=scoring())`, `cv_report` devuelve `mae` y `rmse` **positivos** (≥ 0) e iguales a los de `regression_metrics` en cada pliegue; `regression_metrics` y `evaluate_folds` también dan MAE y RMSE ≥ 0
- [ ] T012 [P] [US2] `test_evaluate_folds_groups_by_school`: con `GroupKFold(5)`, una fila por pliegue con `mae`, `rmse`, `r2`, `fit_seconds`; ninguna sede está en entrenamiento y validación del mismo pliegue
- [ ] T013 [P] [US2] `test_baseline_mae_is_median_rule`: el MAE de la línea base en `evaluate_folds` es igual al de predecir la mediana del entrenamiento de cada pliegue, calculado a mano
- [ ] T014 [P] [US2] `test_evaluate_returns_mean_and_std`: `evaluate` devuelve `mae_mean`, `mae_std`, `rmse_mean`, `r2_mean`, `fit_seconds`

### Implementación

- [ ] T015 [US2] Implementar `candidates`, `scoring`, `cv_report`, `regression_metrics`, `evaluate_folds` y `evaluate` en `src/proyecto/models/train.py` (parámetros de `research.md` §2)
- [ ] T016 [US2] `PYTHONUTF8=1 python -m pytest tests/test_models.py` → T009–T014 en verde (los candidatos de boosting se crean, no se entrenan, para que la prueba sea rápida)

---

## Phase 4: Polish

- [ ] T017 `PYTHONUTF8=1 python -m pytest tests` en verde
- [ ] T018 [P] Revisar con `auditor-de-fuga` (que `evaluate_folds` agrupe por sede y nada lea la prueba) y con `checklist-revision-ia.md`

## Dependencies & Execution Order

T001 y la etapa 3 → T002–T003 → US1 (T004–T008) → US2 (T009–T016) → T017–T018. US2 usa `build_pipeline` de US1.

## Implementation Strategy

MVP = US1: con `build_pipeline` ya corre el notebook 04. US2 completa lo que necesita el torneo (notebook 05).
