---

description: "Lista de tareas: registro del modelo, exportación y esquema (etapa 8)"
---

# Tasks: Registro del modelo, exportación y esquema de entrada

**Input**: `specs/006-model-registry/` y `especificaciones/08-registro.md`

**Prerequisites**: etapa 7 cerrada; `models/final_pipeline.joblib` con la huella de `reports/prueba_huellas.json`

**Tests**: se piden (`CLAUDE.md`, regla 9). Cada prueba se escribe antes que su función y debe fallar primero.

## Phase 0: Pendientes de la auditoría de la etapa 7 (hecho antes de este plan, a pedido del grupo)

- [x] T000 H1, H3, H4 y H6 en el notebook 07; re-ejecución sin reevaluar; resultados idénticos byte a byte; H7 y H8 anotados en reports/auditoria_etapa7.md

## Phase 1: Inferencia para regresión (US2)

- [x] T001 [P] [US2] Pruebas en tests/test_inference.py: `test_regression_schema_saves_and_reloads` (21 columnas, categorías, rangos, `task`), `test_schema_median_comes_only_from_given_frame`, `test_predict_score_rejects_missing_column`, `test_predict_score_rejects_out_of_valid_range`, `test_predict_score_rejects_non_numeric`, `test_predict_score_rejects_unknown_closed_category_but_warns_on_municipality`, `test_predict_score_accepts_missing_values`, `test_predict_score_does_not_learn_from_input`
- [x] T002 [US2] Extender `build_schema` y `validate_inputs` en src/proyecto/inference/schema.py y predict.py; agregar `predict_score`
- [x] T003 [US2] `PYTHONUTF8=1 python -m pytest tests/test_inference.py` en verde

## Phase 2: Registro (US1)

- [x] T004 [US1] Notebook 08: conexión (exigir «databricks»), experimento `saber11-modelo-final`, verificar huella y cargar `final_pipeline.joblib` y `07_metricas_test.json` (detenerse si faltan)
- [x] T005 [US1] Notebook 08: registrar `saber11_puntaje_global` con cloudpickle, parámetros, métricas con intervalos, firma y ejemplo de 21 columnas del entrenamiento (assert: sin sede, sin prohibidas, sin objetivo), etiquetas (etapa, fecha, commit)
- [x] T006 [US1] Notebook 08: alias `champion` y ida y vuelta exacta (500 filas del entrenamiento)

## Phase 3: Exportación y esquema (US2)

- [x] T007 [US2] Notebook 08: exportar `models/model.joblib` desde `champion`; escribir `models/input_schema.json` con el entrenamiento y los rangos válidos aprobados; comprobar que ninguno está en .gitignore
- [x] T008 [US2] Notebook 08: comprobación de que el exportado es el evaluado (opción aprobada por el grupo) y MAE 33,316
- [x] T009 [US2] Notebook 08: pruebas de humo de `predict_score` con una fila normal, una incompleta y una imposible; prueba en tests/test_inference.py con una fila real del entrenamiento y `models/model.joblib`

## Phase 4: Documentación y cierre (US3)

- [x] T010 [US3] models/ficha_modelo.md y reports/08_registro.md (+ 08_registro.json) con cifras de los reportes
- [x] T011 Actualizar reports/documentacion_proyecto.md (regla 10 de CLAUDE.md) y especificacion-proyecto.md §7
- [x] T012 Lanzar `auditor-de-fuga` sobre lo nuevo y guardar reports/auditoria_etapa8.md
- [x] T013 pytest completo; quitar los «View run» del notebook; buscar correos, dirección del espacio de trabajo y tokens en lo que se sube; commit y push a `origin main`
