# Implementation Plan: Optimización de los finalistas con seguimiento (tuning.py)

**Branch**: `004-hyperparameter-tuning` (trabajo en `main`) | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-hyperparameter-tuning/spec.md` y `especificaciones/06-optimizacion.md`

## Summary

Crear `src/proyecto/models/tuning.py` con la estructura del `tuning.py` del profesor, adaptado de clasificación con costos a
**regresión con MAE**: espacios de búsqueda de HistGradientBoosting y XGBoost (con `min_frequency` y la pérdida como
parámetros), fábricas de modelos, parámetros de partida del torneo, `reserve_groups` (25 % de sedes), `tune` (Optuna TPE,
minimiza el MAE, cada ensayo anidado en MLflow, estudio reanudable en sqlite) y bootstrap **por sede** del MAE y de la
diferencia de MAE. Se quitan matriz de costos, probabilidades, AUC, F1 y regla de decisión. Pruebas en
`tests/test_tuning.py`; el notebook 06 orquesta y el informe `reports/06_optimizacion.md` se llena con sus cifras.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: optuna 5.0.0, mlflow 3.17.1, scikit-learn 1.9.1, xgboost 3.4.1, pandas 3.0.6 (ya en `requirements.txt`; no se instala nada)

**Storage**: estudio de Optuna en `optuna_06.db` (sqlite, raíz, ignorado por Git); MLflow en Databricks o `mlflow_local.db`

**Testing**: pytest con tablas hechas a mano y modelos diminutos (pocos árboles) para que corran en segundos

**Target Platform**: Windows local del grupo (8 núcleos)

**Project Type**: librería interna (`src/proyecto/models/`) + notebook que orquesta

**Performance Goals**: búsqueda completa < 30 min (medido: un ajuste ~4–10 s HGB y ~2–3 s XGB sobre ~29.000 estudiantes)

**Constraints**: `test.joblib` cerrado; validación siempre agrupada por sede; preprocesamiento dentro del `Pipeline`

**Scale/Scope**: 1 módulo (~170 líneas), 1 archivo de pruebas (~8 pruebas), 1 notebook, 1 informe

## Constitution Check

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| I. Datos originales intactos | ✅ | Solo lee `data/processed/train.joblib` |
| II. Partir por la unidad de análisis | ✅ | Reserva con `split_by_group`, pliegues con `group_cv`, bootstrap por sede; pruebas lo verifican |
| III. La prueba se abre una sola vez | ✅ | Nada lee `test.joblib`; toda la comparación es dentro del entrenamiento |
| IV. Decisiones con motivo | ✅ | Rangos con motivo en la especificación de etapa; decisiones en `reports/06_optimizacion.md` |
| V. Nada sensible sale | ✅ | Se registran solo parámetros y métricas; `.env` no se imprime |
| VI. El código es nuestro | ✅ | Estructura del ejemplo, español en textos, inglés en nombres |
| VII. No se inventan datos | ✅ | El informe solo usa cifras impresas por el notebook |

## Project Structure

```text
specs/004-hyperparameter-tuning/  spec.md · plan.md · research.md · data-model.md · quickstart.md · contracts/tuning.md · tasks.md
especificaciones/06-optimizacion.md   # guía de la etapa (entrada)
src/proyecto/models/tuning.py         # NUEVO
tests/test_tuning.py                  # NUEVO
notebooks/06_optimizacion.ipynb       # se completa (hoy es esqueleto)
reports/06_optimizacion.md            # se completa; + 06_best_params.json y 06_comprobacion.csv
reports/auditoria_etapa6.md           # informe del auditor-de-fuga
.gitignore                            # + optuna_*.db
```

**Structure Decision**: estructura obligatoria de `CLAUDE.md`. `train.py` no cambia: `tuning.py` reutiliza `build_pipeline`,
`evaluate_folds`, `regression_metrics` y `feature_frame`.

## Dependencias y orden

1. `data/processed/train.joblib` regenerado con el notebook 03 (hecho el 5 nov 2026: 57.286 estudiantes, 1.155 sedes).
2. `tuning.py` + pruebas (pytest en verde).
3. Notebook 06 ejecutado completo (búsqueda + comprobación), midiendo el tiempo.
4. Informe, decisión en `especificacion-proyecto.md` §7, auditoría, commit y push.

## Decisiones del grupo (5 nov 2026, antes de ejecutar)

- Presupuesto aprobado: 25 (HGB) + 30 (XGB) ensayos, 3 pliegues por sede (`research.md` §3). Partida medida con los mismos
  pliegues y datos de la búsqueda; el informe aclara que no se compara directamente con el 33,56 del torneo.
- Regla 2: si el intervalo entre finalistas incluye el cero, se elige HistGradientBoosting; si no, el de menor MAE.

## Complexity Tracking

Sin violaciones de la constitución.
