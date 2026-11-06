---

description: "Lista de tareas: validación final e interpretación (evaluation.py)"
---

# Tasks: Validación final e interpretación (evaluation.py)

**Input**: `specs/005-validation/` y `especificaciones/07-validacion.md`

**Prerequisites**: etapa 6 cerrada (`reports/06_best_params.json`); `data/processed/train.joblib` y `test.joblib`

**Tests**: se piden (`CLAUDE.md`, regla 9). Cada prueba se escribe antes que su función y debe fallar primero.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [x] T001 Agregar `data/processed/*` ya está ignorado; verificar que `models/final_pipeline.joblib` sigue en `.gitignore`
- [x] T002 Crear `src/proyecto/models/evaluation.py` con docstring en español (qué hace, que no abre la prueba por sí mismo) e importar `feature_columns` de `engineering.py`
- [x] T003 [P] Crear `tests/test_evaluation.py` reutilizando `_frame` de `tests/test_models.py`

## Phase 2: User Story 1 - Medir con la prueba, una vez (P1) 🎯 MVP

- [x] T004 [P] [US1] `test_metric_difference_point_value_and_groups` en tests/test_evaluation.py: valor puntual = RMSE(A) − RMSE(B) y R²(A) − R²(B); con una sola sede el intervalo no tiene ancho; con A = B el intervalo es [0; 0]
- [x] T005 [US1] Implementar `bootstrap_metric_difference` en src/proyecto/models/evaluation.py
- [x] T006 [US1] Notebook 07, secciones 0–4: cargar train; congelar decisiones a `reports/07_decisiones_congeladas.json` con fecha y hora; entrenar el modelo final con todo el entrenamiento (`build_tuned_pipeline` con los parámetros de `06_best_params.json`) y la línea base; abrir la prueba una vez (marca + `data/processed/prueba_resultados.joblib`); métricas, intervalos, diferencias y metas

## Phase 3: User Story 2 - Equidad por segmento (P1)

- [x] T007 [P] [US2] `test_stratum_segment_labels`: «Sin Estrato», «Sin dato (vacío)» y estratos 1–6 bien asignados, ningún vacío como estrato 0
- [x] T008 [P] [US2] `test_equity_table_counts_and_rule`: conteos de estudiantes y sedes, MAE por segmento, `cumple` falso cuando hay empate exacto o el modelo es peor; `veredicto` «con ventaja clara» / «sin ventaja concluyente» / «no cumple» según el intervalo
- [x] T009 [US2] Implementar `stratum_segment`, `equity_segments` y `equity_table` en src/proyecto/models/evaluation.py
- [x] T010 [US2] Notebook 07, sección 5: tabla de equidad (estrato, zona, naturaleza, género) y lista de segmentos que cumplen y que no

## Phase 4: User Story 3 - Interpretación (P2)

- [x] T011 [P] [US3] `test_permutation_importance_detects_signal`: ~0 para una columna sin efecto, > 0 para la que define el objetivo; `model_columns` no incluye la sede ni el objetivo
- [x] T012 [US3] Implementar `model_columns` y `permutation_importance_table` en src/proyecto/models/evaluation.py
- [x] T013 [US3] Notebook 07, sección 6: importancia por permutación sobre la prueba (guardada junto a las predicciones), gráfico y atributos sensibles
- [x] T014 `PYTHONUTF8=1 python -m pytest` completo en verde

## Phase 5: Cierre

- [x] T015 Ejecutar el notebook 07 completo (una sola apertura de la prueba) y guardar `reports/07_metricas_test.json`, `07_equidad.csv`, `07_importancia.csv`
- [x] T016 Completar reports/07_validacion.md solo con cifras de la ejecución; declarar los segmentos que no cumplen
- [x] T017 Anotar el resultado en la sección 7 de especificacion-proyecto.md
- [x] T018 Lanzar `auditor-de-fuga` sobre evaluation.py y el notebook 07; guardar en reports/auditoria_etapa7.md
- [x] T019 pytest en verde; commit y push a `origin main`

## Dependencies

Setup → US1 → US2 → US3 → Cierre. La prueba se abre solo en T015 (las celdas se escriben antes, sin ejecutarlas contra la prueba).
