# Implementation Plan: Pipeline de modelo, candidatos y métricas (train.py)

**Branch**: `003-model-training` (trabajo en `main`) | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-model-training/spec.md`

## Summary

Crear `src/proyecto/models/train.py` con la estructura del `train.py` del profesor, adaptado de clasificación con matriz de
costos a **regresión con MAE**: `candidates()` (línea base por mediana, Ridge, Random Forest, HistGradientBoosting, XGBoost),
`build_pipeline(modelo)` (variables nuevas opcionales → preprocesador de la etapa 4 → modelo), `scoring()` para
`cross_validate`, `regression_metrics`, `evaluate_folds`/`evaluate` agrupados por sede y `feature_frame`. Se quitan la
matriz de costos, la regla de decisión y las métricas de clasificación. Pruebas en `tests/test_models.py`.

## Technical Context

**Language/Version**: Python 3.12.10

**Primary Dependencies**: scikit-learn 1.9.1, xgboost 3.4.1, pandas 3.0.6 (fijadas en `requirements.txt`)

**Storage**: N/A

**Testing**: pytest 9.1.1 con tablas hechas a mano (modelos pequeños para que corran rápido)

**Target Platform**: Windows local del grupo; Streamlit Community Cloud (la app carga el Pipeline guardado)

**Project Type**: librería interna (`src/proyecto/models/`)

**Performance Goals**: las pruebas corren en segundos

**Constraints**: todo lo que aprende de los datos va dentro del `Pipeline`; validación siempre agrupada por sede

**Scale/Scope**: 1 módulo (~120 líneas), 1 archivo de pruebas (~10 pruebas)

**Entorno**: `import lightgbm` falla en este equipo (falta `vcomp140.dll`) y el grupo no puede instalar el Visual C++
Redistributable; por eso LightGBM se reemplaza por `HistGradientBoostingRegressor` (`research.md` §4).

## Constitution Check

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| I. Datos originales intactos | ✅ | No lee ni escribe datos |
| II. Partir por la unidad de análisis | ✅ | `evaluate_folds` agrupa por `cole_cod_dane_sede`; una prueba verifica que no se comparten sedes |
| III. La prueba se abre una sola vez | ✅ | Nada aquí lee `test.joblib`; el preprocesamiento queda dentro del `Pipeline` |
| IV. Decisiones con motivo | ✅ | Candidatos y parámetros justificados en `research.md` |
| V. Nada sensible sale | ✅ | Pruebas con datos inventados |
| VI. El código es nuestro | ✅ | Estructura del ejemplo; español en textos, inglés en nombres |
| VII. No se inventan datos | ✅ | Ninguna cifra nueva; la línea base 42,8 viene del caso |

## Project Structure

```text
specs/003-model-training/   plan.md · research.md · quickstart.md · contracts/train.md · checklists/ · tasks.md
src/proyecto/models/
├── __init__.py             # ya existe
└── train.py                # NUEVO
tests/
└── test_models.py          # NUEVO
```

**Structure Decision**: estructura obligatoria de `CLAUDE.md`.

## Dependencias y orden

1. ~~Instalar el Visual C++ Redistributable x64~~: no se pudo (sin permisos de administrador); LightGBM se reemplaza.
2. **Etapa 3 implementada** (`split.py` define `GROUP_COL`). Su plan está pendiente de aprobación.
3. Luego esta pieza. Después, los notebooks 04 y 05 pueden correr.

## Decisiones del grupo (31 oct 2026)

- Aprobados los 5 candidatos con los parámetros de partida del ejemplo.
- Los dos boosting con su pérdida por defecto en el torneo; error absoluto en la etapa 6.
- **LightGBM reemplazado por `HistGradientBoostingRegressor`** (31 oct 2026): usa la misma técnica que LightGBM (boosting con histogramas), no requiere instalar nada adicional y funciona en el equipo de todos los integrantes, lo que cuida la reproducibilidad. XGBoost se mantiene.
  Reemplaza la decisión anterior de instalar el Visual C++ Redistributable, que no se pudo por falta de permisos.
- `evaluate_folds` y `evaluate` lanzan `ValueError` si falta `cole_cod_dane_sede` (protección acordada por el grupo).
- MAE y RMSE se reportan en positivo, con prueba. **Diseño confirmado por el grupo** (`research.md` §3): `scoring()`
  sigue negativo para no invertir la búsqueda de la etapa 6, y `cv_report` / `regression_metrics` muestran positivos.
- Orden: primero la etapa 3; después esta pieza.

## Complexity Tracking

Sin violaciones: no aplica.
