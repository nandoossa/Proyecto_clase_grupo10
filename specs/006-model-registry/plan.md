# Implementation Plan: Registro del modelo, exportación y esquema de entrada

**Branch**: `006-model-registry` (trabajo en `main`) | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

## Summary

El notebook 08 verifica la huella de `final_pipeline.joblib`, lo registra en Unity Catalog con parámetros, métricas de la
prueba con intervalos, firma y ejemplo de 21 columnas del entrenamiento y etiquetas de origen; pone el alias `champion`;
comprueba la ida y vuelta; exporta `models/model.joblib` desde `champion` y escribe `models/input_schema.json`. `schema.py`
y `predict.py` se extienden a regresión (sin romper las funciones de clasificación de la plantilla, que usa la app hasta la
etapa 9). Pruebas nuevas en `tests/test_inference.py`. Ficha del modelo, informe y documentación general.

## Technical Context

**Language/Version**: Python 3.12 · **Dependencies**: mlflow 3.17.1, scikit-learn 1.9.1 (ya instaladas)

**Storage**: Unity Catalog en Databricks; `models/model.joblib` y `models/input_schema.json` en el repo

**Testing**: pytest con datos inventados y una fila real del entrenamiento

**Constraints**: la prueba no se vuelve a evaluar; ningún dato sensible en lo que se sube

**Scale/Scope**: `schema.py` y `predict.py` (+~60 líneas), ~6 pruebas, 1 notebook, 2 informes

## Constitution Check

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| I. Datos originales intactos | ✅ | Solo lee `data/processed/` |
| II. Partir por la unidad de análisis | ✅ | No hay partición nueva; la firma excluye la sede |
| III. La prueba se abre una sola vez | ✅ | Métricas de la prueba copiadas de `07_metricas_test.json`; ver la decisión 1 |
| IV. Decisiones con motivo | ✅ | `reports/08_registro.md` |
| V. Nada sensible sale | ✅ | Búsqueda de correos, dirección del espacio de trabajo y tokens antes del commit; se quitan los «View run» |
| VI. El código es nuestro | ✅ | Español en textos, inglés en nombres |
| VII. No se inventan datos | ✅ | Versión y nombre salen de la ejecución |

## Project Structure

```text
especificaciones/08-registro.md · specs/006-model-registry/{spec,plan,research,quickstart,tasks}.md · contracts/inference.md
src/proyecto/inference/schema.py, predict.py     # se extienden a regresión
tests/test_inference.py                          # pruebas nuevas
notebooks/08_registro_modelo.ipynb               # se completa (registro + exportación + esquema)
models/model.joblib, models/input_schema.json, models/ficha_modelo.md
reports/08_registro.md, reports/08_registro.json, reports/auditoria_etapa8.md
```

## Decisiones del grupo (5 nov 2026, antes de implementar)

1. **Exportado = evaluado, opción A:** huella del modelo, predicciones idénticas a `final_pipeline.joblib` en las 57.286
   filas del entrenamiento y MAE 33,316 recalculado con las predicciones y etiquetas guardadas. **No se vuelve a predecir
   sobre la prueba.**
2. **Rangos válidos:** edad 13–80 (el rango visto en el entrenamiento), estrato 1–6, personas 1–5, cuartos 1–6, marca 0–1.
   Los campos con vacíos en el entrenamiento aceptan «sin respuesta»; `input_schema.json` los marca (`nullable`).
3. **Categorías nuevas:** se rechazan en las 14 listas cerradas; solo se advierte en los 2 códigos de municipio.
4. **Predicción:** `predict_score` con la columna `puntaje_estimado`, sin redondear ni recortar. Las funciones de
   clasificación se conservan hasta la etapa 9 y se quitarán allí.
