---

description: "Lista de tareas: inferencia de regresión y app de Streamlit (etapa 9)"
---

# Tasks: Inferencia de regresión y app de Streamlit

**Input**: `specs/007-app-inference/` y `especificaciones/09-app.md`

**Prerequisites**: etapa 8 cerrada (`models/model.joblib`, `models/input_schema.json`); respuestas del grupo a P1–P4 del plan

**Tests**: se piden (`CLAUDE.md`, regla 9). Cada prueba se escribe antes que su función y debe fallar primero.

## Phase 1: Inferencia solo de regresión (US3)

- [x] T001 [US3] En tests/test_inference.py: quitar las pruebas y el modelo de juguete de clasificación; agregar `test_classification_functions_removed` y `test_validate_requires_regression_schema`
- [x] T002 [US3] En src/proyecto/inference/predict.py: quitar `predict_with_scores`, `decide_min_cost`, `_ordered_proba` y la rama de clasificación; actualizar el docstring
- [x] T003 [US3] `PYTHONUTF8=1 python -m pytest tests/test_inference.py` en verde

## Phase 2: App (US1, US2)

- [x] T004 [P] [US1] tests/test_app.py: pruebas de `form_to_row` (en src/proyecto/inference/form.py) (personas y cuartos en texto → códigos; «Sin estrato» → vacío + `sin_estrato`=1; «Sin respuesta» → vacío y `sin_estrato`=0; edad inválida y obligatorio vacío → `InputValidationError` con el nombre del campo)
- [x] T005 [P] [US1] tests/test_app.py con AppTest: carga con título y aviso visible; perfil normal → puntaje entero en [100, 477] y error típico; «Sin respuesta» en los 12 campos → puntaje; sin `mlflow`/`databricks`/`token` en el código
- [x] T006 [P] [US2] tests/test_app.py con AppTest: edad 12 y 81 → mensaje que nombra la edad (con el campo numérico de P1 no se puede escribir «abc»), sin puntaje; obligatorio vacío → mensaje que lo nombra
- [x] T007 [US1] (Solo si se aprueba P2) agregar `municipality_names` a models/input_schema.json, calculado con el entrenamiento
- [x] T008 [US1] Reescribir app/streamlit_app.py (las funciones `LABELS`, `form_to_row` y `reference_range` quedaron en src/proyecto/inference/form.py): formulario en 3 secciones, resultado, mensajes de corrección y aviso de uso responsable
- [x] T009 [US1] `PYTHONUTF8=1 python -m pytest tests/test_app.py` en verde; `streamlit run app/streamlit_app.py` abre en local

## Phase 3: Notebook 09 (US3)

- [x] T010 [US3] Reemplazar las celdas de la plantilla de notebooks/09_inferencia.ipynb: modelo y esquema, 4 perfiles inventados con `form_to_row`, un ejemplo rechazado; sin Databricks ni la prueba
- [x] T011 [US3] Ejecutar el notebook 09 de principio a fin

## Phase 4: Documentación, revisión y cierre

- [x] T012 reports/09_despliegue.md sin desplegar (decisiones, pruebas locales con resultados reales, plan de despliegue y plan B)
- [x] T013 reports/documentacion_proyecto.md (regla 10 de CLAUDE.md) y especificacion-proyecto.md §7
- [x] T014 Lanzar `auditor-de-fuga` sobre lo nuevo y guardar reports/auditoria_etapa9.md, con la búsqueda de datos sensibles (`.env`, tokens, correos, direcciones del espacio de trabajo, datos de estudiantes) en lo que se sube
- [x] T015 pytest completo; marcar las casillas de especificaciones/09-app.md que se vean funcionando; commit y push a `origin main`

## Dependencies & Execution Order

Respuestas a P1–P4 → Phase 1 → Phase 2 (T004–T006 antes de T008; T007 antes de T008) → Phase 3 (usa `form_to_row`) →
Phase 4.
