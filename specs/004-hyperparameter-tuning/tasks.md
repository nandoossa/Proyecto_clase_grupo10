---

description: "Lista de tareas: tuning.py (optimización de los finalistas con seguimiento)"
---

# Tasks: Optimización de los finalistas con seguimiento (tuning.py)

**Input**: Design documents from `/specs/004-hyperparameter-tuning/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/tuning.md, `especificaciones/06-optimizacion.md`;
`data/processed/train.joblib` regenerado (notebook 03)

**Tests**: se piden (`CLAUDE.md`, regla 9, y el pedido del grupo). Cada prueba se escribe antes que su función y debe fallar primero.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [x] T001 Agregar `optuna_*.db` a `.gitignore` (junto a `mlflow_local.db`): el estudio se regenera y no se sube
- [x] T002 Crear `src/proyecto/models/tuning.py` con docstring en español (qué cambia respecto del ejemplo: regresión con MAE, sin costos ni probabilidades, LightGBM → HistGradientBoosting) e importar `build_pipeline`, `candidates`, `evaluate_folds` de `train.py`, `split_by_group`, `RANDOM_STATE` de `split.py` y `log_run` de `mlflow_utils.py`
- [x] T003 [P] Crear `tests/test_tuning.py` con un ayudante `_frame(n_sedes, por_sede, seed)` que arma una tabla inventada con las columnas de la etapa 3 y `cole_cod_dane_sede` (puede reutilizar el de `tests/test_models.py` si existe)

---

## Phase 2: User Story 1 - Buscar mejores parámetros sin tocar la prueba (P1) 🎯 MVP

**Goal**: espacios de búsqueda, fábricas, parámetros de partida y `tune` reanudable.

**Independent Test**: `pytest tests/test_tuning.py -k "space or tune"`.

### Pruebas (primero; deben fallar)

- [x] T004 [P] [US1] `test_spaces_return_params_in_range`: con 20 ensayos de un estudio aleatorio, cada parámetro de `hgb_space` y `xgb_space` cae en su rango de `especificaciones/06-optimizacion.md` §4; `min_frequency` ∈ {0.01, 0.001}; pérdida ∈ {cuadrática, absoluta} en tests/test_tuning.py
- [x] T005 [P] [US1] `test_factories_build_models_that_fit`: para cada modelo, `build_tuned_pipeline(name, params)` con parámetros del espacio (y con `STARTING_PARAMS`) se ajusta en la tabla inventada y predice sin vacíos; `min_frequency` llega al preprocesador en tests/test_tuning.py
- [x] T006 [P] [US1] `test_starting_params_match_tournament`: `make_*(STARTING_PARAMS[name])` tiene los mismos parámetros que el modelo de `candidates()` en tests/test_tuning.py
- [x] T007 [P] [US1] `test_tune_minimizes_mae_and_resumes`: `tune(..., n_trials=2, log=False, storage=tmp)` deja 2 ensayos, dirección minimize, `start_mae` guardado; llamarla otra vez con `n_trials=3` solo agrega 1 en tests/test_tuning.py

### Implementación

- [x] T008 [US1] Implementar `hgb_space`, `xgb_space`, `make_hgb`, `make_xgb`, `STARTING_PARAMS`, `MODELS`, `build_tuned_pipeline` en src/proyecto/models/tuning.py (contrato `contracts/tuning.md`)
- [x] T009 [US1] Implementar `tune` en src/proyecto/models/tuning.py: mide partida con los mismos pliegues (ejecución `<modelo>-partida`), Optuna TPE semilla 42 `direction="minimize"` sobre el MAE medio; cada ensayo anidado en MLflow con `mae`, `rmse`, `r2`, sus `_std` y `fit_seconds`, etiquetas `etapa`, `modelo`, `metrica_optimizada=mae`; `storage` sqlite con `load_if_exists`
- [x] T010 [US1] `PYTHONUTF8=1 python -m pytest tests/test_tuning.py` → T004–T007 en verde

---

## Phase 3: User Story 2 - Comprobar en sedes que la búsqueda no vio (P1)

**Independent Test**: `pytest tests/test_tuning.py -k "reserve or bootstrap"`.

### Pruebas (primero; deben fallar)

- [x] T011 [P] [US2] `test_reserve_groups_disjoint`: `reserve_groups(df)` no comparte ninguna sede y reserva ~25 % de las sedes; todas las filas quedan en algún lado en tests/test_tuning.py
- [x] T012 [P] [US2] `test_bootstrap_difference_point_value`: el valor puntual es exactamente MAE(A) − MAE(B); con A = B el intervalo es [0; 0] en tests/test_tuning.py
- [x] T013 [P] [US2] `test_bootstrap_resamples_whole_sedes`: con una sola sede (errores distintos por fila) el intervalo de la diferencia y del MAE no tiene ancho (remuestrear filas sí lo tendría); con sedes de errores muy distintos sí tiene ancho en tests/test_tuning.py

### Implementación

- [x] T014 [US2] Implementar `reserve_groups`, `bootstrap_mae_difference` y `bootstrap_metric_ci` en src/proyecto/models/tuning.py
- [x] T015 [US2] `PYTHONUTF8=1 python -m pytest tests/test_tuning.py` → T004–T013 en verde, y `python -m pytest` completo en verde

---

## Phase 4: User Story 3 - Notebook, registro e informe (P2)

- [x] T016 [US3] Completar notebooks/06_optimizacion.ipynb siguiendo el ejemplo: configuración (`configure_mlflow()`, `set_experiment("saber11-optimizacion")`, aviso si quedó local), carga de `train.joblib` (sin abrir `test.joblib`), reserva de sedes con comprobación de 0 sedes compartidas, reglas de decisión escritas **antes** de los resultados, búsqueda con presupuesto 25 + 30 y tiempo medido, gráfico del mejor-hasta-ahora, importancia de parámetros, comprobación en la reserva (MAE, RMSE, R², diferencias con IC 95 % por sede, comparación entre finalistas), consulta de MLflow y guardado de `reports/06_best_params.json` y `reports/06_comprobacion.csv`
- [x] T017 [US3] Ejecutar el notebook completo en sitio (`jupyter nbconvert --execute --inplace`) y comprobar que tarda < 30 min y que MLflow tiene 1 ejecución por ensayo (hecho con Databricks: 55 ensayos registrados; búsqueda 31,1 min, por encima del objetivo por el registro por red; en local 27,2 min)
- [x] T018 [US3] Completar reports/06_optimizacion.md solo con cifras de la salida del notebook (mejor modelo, parámetros, MAE antes y después con referencia 33,56, comprobación con IC, decisiones)
- [x] T019 [US3] Anotar la decisión en la sección 7 de especificacion-proyecto.md y marcar las casillas cumplidas de especificaciones/06-optimizacion.md

---

## Phase 5: Polish

- [x] T020 Lanzar el subagente `auditor-de-fuga` sobre src/proyecto/models/tuning.py y notebooks/06_optimizacion.ipynb y guardar su informe en reports/auditoria_etapa6.md
- [x] T021 `python -m pytest` completo en verde; commit y push a `origin main`

## Dependencies

- Setup → US1 → US2 (las pruebas de US2 son independientes, pero comparten archivo) → US3 → Polish.
- Paralelo: T004–T007 entre sí; T011–T013 entre sí.

## Implementation Strategy

MVP = US1 + US2 (módulo probado). US3 corre la búsqueda real y produce el informe.
