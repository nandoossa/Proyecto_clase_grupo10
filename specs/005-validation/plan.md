# Implementation Plan: Validación final e interpretación (evaluation.py)

**Branch**: `005-validation` (trabajo en `main`) | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: `specs/005-validation/spec.md` y `especificaciones/07-validacion.md`

## Summary

Crear `src/proyecto/models/evaluation.py` con lo reutilizable de la validación: segmentos de equidad (estrato con «Sin
Estrato» y vacíos, zona, naturaleza, género), tabla de equidad con intervalo por sedes, diferencia de cualquier métrica con
intervalo por sedes (para RMSE y R²; el MAE ya lo da `tuning.bootstrap_mae_difference`) e importancia por permutación por
columna original. El notebook 07 congela las decisiones con fecha, entrena el modelo final con todo el entrenamiento, abre la
prueba **una vez** (marca + resultados guardados para no reevaluar), mide, compara con la línea base y las metas, revisa la
equidad e interpreta. Pruebas en `tests/test_evaluation.py`.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: scikit-learn 1.9.1 (`permutation_importance`, `DummyRegressor`), pandas, numpy; reutiliza `train.py`
y `tuning.py`. No se instala nada (no se usa SHAP: la importancia por permutación es lo pedido y no depende del tipo de modelo).

**Storage**: `data/processed/prueba_resultados.joblib` (predicciones e importancias de la prueba; ignorado por Git),
`models/final_pipeline.joblib` (ignorado por Git); salidas pequeñas en `reports/`.

**Testing**: pytest con datos inventados y modelos diminutos

**Target Platform**: Windows local del grupo

**Project Type**: librería interna + notebook que orquesta

**Performance Goals**: notebook completo en pocos minutos (un ajuste del modelo final ~20–40 s; permutación 21 columnas × 5)

**Constraints**: la prueba se abre una vez y no se decide nada con ella; intervalos por sede

**Scale/Scope**: 1 módulo (~110 líneas), 1 archivo de pruebas (~7 pruebas), 1 notebook, 1 informe

## Constitution Check

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| I. Datos originales intactos | ✅ | Solo lee `data/processed/` |
| II. Partir por la unidad de análisis | ✅ | Intervalos remuestreando sedes; la prueba es de sedes no vistas (etapa 3) |
| III. La prueba se abre una sola vez | ✅ | Decisiones congeladas antes; marca y resultados guardados; nada se ajusta después |
| IV. Decisiones con motivo | ✅ | `reports/07_validacion.md` y `07_decisiones_congeladas.json` |
| V. Nada sensible sale | ✅ | Solo métricas agregadas por segmento; ningún estudiante individual en los reportes |
| VI. El código es nuestro | ✅ | Español en textos, inglés en nombres |
| VII. No se inventan datos | ✅ | El informe usa solo cifras impresas por el notebook |

## Project Structure

```text
specs/005-validation/          spec.md · plan.md · research.md · quickstart.md · contracts/evaluation.md · tasks.md
especificaciones/07-validacion.md
src/proyecto/models/evaluation.py     # NUEVO
tests/test_evaluation.py              # NUEVO
notebooks/07_validacion_interpretacion.ipynb   # se completa
reports/07_validacion.md (+ 07_decisiones_congeladas.json, prueba_abierta.txt, 07_metricas_test.json, 07_equidad.csv, 07_importancia.csv)
reports/auditoria_etapa7.md
```

## Decisiones que el grupo debe confirmar antes de abrir la prueba

1. Las decisiones congeladas de `especificaciones/07-validacion.md` §1 (modelo, parámetros, línea base, metas).
2. La regla de equidad (§4): «cumple» = MAE del modelo **estrictamente menor** que el de la línea base en el segmento; el
   intervalo es informativo y no cambia la regla.

## Complexity Tracking

Sin violaciones.
