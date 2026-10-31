# Feature Specification: Pipeline de modelo, candidatos y métricas (train.py)

**Feature Branch**: `003-model-training` (se trabaja en `main`)

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Hacer `src/proyecto/models/train.py` basado en el ejemplo del profesor
(`material-del-curso/ejemplo-creditsight/src/creditsight/models/train.py`)", adaptado a regresión con MAE.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unir variables, preprocesamiento y modelo en un solo Pipeline (Priority: P1)

Los notebooks 04 a 07 necesitan `build_pipeline(modelo)`: un objeto que reciba la tabla de entrenamiento (con `punt_global`
ya separado) y haga, en orden, variables nuevas (si se encienden) → preprocesamiento de la etapa 4 → modelo, ajustándose
solo con los datos que recibe.

**Why this priority**: sin esto no se puede medir nada en el notebook 04 (variables) ni en el 05 (torneo).

**Independent Test**: con una tabla hecha a mano, el Pipeline se ajusta y predice números sin vacíos; con
`use_engineered=True` aparece el paso de variables nuevas.

**Acceptance Scenarios**:

1. **Given** una tabla con las columnas de la etapa 3 (incluida `cole_cod_dane_sede`), **When** se ajusta
   `build_pipeline(modelo)`, **Then** predice un número por fila, sin vacíos.
2. **Given** dos tablas iguales salvo en `cole_cod_dane_sede`, **When** se predice con el mismo Pipeline, **Then** las
   predicciones son idénticas (la sede no influye).

---

### User Story 2 - Comparar candidatos con la misma vara (Priority: P1)

El torneo necesita una lista fija de modelos de regresión, incluida la línea base (predecir siempre la mediana, MAE 42,8 en
el caso de negocio), y las métricas MAE (principal), RMSE y R² calculadas igual para todos, con validación agrupada por sede.

**Why this priority**: es la comparación que decide el modelo; si la vara cambia entre modelos, el torneo no vale.

**Independent Test**: con valores conocidos, las métricas dan lo esperado; la evaluación por pliegues nunca comparte sedes.

**Acceptance Scenarios**:

1. **Given** predicciones perfectas, **When** se calculan las métricas, **Then** MAE = 0, RMSE = 0 y R² = 1.
2. **Given** la línea base, **When** se evalúa, **Then** su MAE es el de predecir la mediana del entrenamiento de cada pliegue.
3. **Given** `cross_validate(..., scoring=scoring())`, **When** se lee el MAE, **Then** se sabe que viene negativo
   (convención de scikit-learn) y hay que cambiarle el signo.

### Edge Cases

- Una sede con un solo estudiante: va completa a un pliegue.
- Un municipio nunca visto en un pliegue de validación: el preprocesador lo manda a «poco frecuente» (etapa 4).
- Falta `cole_cod_dane_sede` en la tabla que llega a `evaluate_folds`: error claro (`ValueError`), no una partición por fila.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `build_pipeline(model, scale=True, use_engineered=False, extra_numeric=None, min_frequency=0.01)` MUST devolver
  un `Pipeline` [variables nuevas si `use_engineered`] → `build_preprocessor(...)` → modelo, y funcionar llamado solo con
  `build_pipeline(modelo)` (así lo llaman los notebooks).
- **FR-002**: `candidates()` MUST devolver los modelos del torneo con la marca de si necesitan escalado: línea base
  (mediana), Ridge, Random Forest, HistGradientBoosting (en lugar de LightGBM) y XGBoost, todos de **regresión**, con
  semilla 42.
- **FR-003**: `scoring()` MUST devolver el diccionario para `cross_validate`: MAE, RMSE y R²; `cv_report` MUST mostrar
  MAE y RMSE en positivo (decisión del grupo, 31 oct 2026).
- **FR-004**: `regression_metrics(y_true, y_pred)` MUST devolver MAE, RMSE y R² (en puntos, positivos).
- **FR-005**: `evaluate_folds(pipeline, X, y, cv)` MUST partir por `cole_cod_dane_sede` y devolver una fila por pliegue con
  las métricas y el tiempo de ajuste; `evaluate` MUST devolver media y desviación entre pliegues. Si falta la columna
  `cole_cod_dane_sede`, los dos MUST lanzar `ValueError`.
- **FR-006**: `feature_frame(df)` MUST separar `X` (sin `punt_global`, conservando `cole_cod_dane_sede` para agrupar) e `y`.
- **FR-007**: Nada de la matriz de costos, la regla de decisión ni las métricas de clasificación del ejemplo.

### Key Entities

- **Candidato**: nombre, modelo sin ajustar, ¿necesita escalado?
- **Resultado por pliegue**: MAE, RMSE, R², segundos de ajuste.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las pruebas de `tests/test_models.py` pasan.
- **SC-002**: Los notebooks 04 y 05 pueden importar `build_pipeline` y `scoring` sin cambiar su forma de llamarlos.
- **SC-003**: 0 sedes compartidas entre entrenamiento y validación en `evaluate_folds`.

## Assumptions

- Los parámetros de partida de los candidatos son los del ejemplo adaptados a regresión; la etapa 6 los optimiza.
- LightGBM no carga en Windows sin el Visual C++ Redistributable, y el grupo no puede instalarlo: se reemplaza por
  `HistGradientBoostingRegressor` (decisión del grupo, 31 oct 2026; `research.md` §4).
- `GROUP_COL` viene de `src/proyecto/data/split.py` (etapa 3, planificada): la etapa 3 se implementa antes.
- La condición de equidad (MAE por segmento) se evalúa en la etapa 7; queda fuera de esta pieza.
- Fuera de alcance: optimización (`tuning.py`, etapa 6) y MLflow.
