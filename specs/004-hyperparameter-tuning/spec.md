# Feature Specification: Optimización de los finalistas con seguimiento (tuning.py)

**Feature Branch**: `004-hyperparameter-tuning` (se trabaja en `main`)

**Created**: 2026-11-05

**Status**: Draft

**Input**: User description: "Optimización de hiperparámetros de los finalistas (HistGradientBoosting y XGBoost) con Optuna y
seguimiento en MLflow: crear `src/proyecto/models/tuning.py`, `tests/test_tuning.py` y completar
`notebooks/06_optimizacion.ipynb`. La entrada completa y las reglas están en `especificaciones/06-optimizacion.md`. Regresión
con MAE (minimize), validación agrupada por sede, reserva del 25 % de sedes, bootstrap por sede, sin abrir `test.joblib`."

> Fuente de las reglas: `especificaciones/06-optimizacion.md` (manda sobre esta especificación si hay diferencia).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Buscar mejores parámetros para cada finalista sin tocar la prueba (Priority: P1)

El grupo quiere saber si los dos finalistas del torneo (HistGradientBoosting, MAE 33,56; XGBoost, 33,66) se equivocan menos
con otros parámetros, probando también las dos decisiones pendientes: el umbral de municipios poco frecuentes (1 % o 0,1 %)
y entrenar con error absoluto en vez de cuadrático. La búsqueda solo usa el 75 % de las sedes del entrenamiento.

**Why this priority**: es el objetivo de la etapa; sin búsqueda no hay nada que comprobar.

**Independent Test**: con una tabla pequeña hecha a mano, la búsqueda corre unos pocos ensayos, cada uno con parámetros
dentro de su rango, y los parámetros de partida se miden con los mismos pliegues.

**Acceptance Scenarios**:

1. **Given** la parte de búsqueda y 3 pliegues por sede, **When** se lanza la búsqueda de un finalista, **Then** cada ensayo
   devuelve el MAE medio entre pliegues y el mejor ensayo es el de menor MAE.
2. **Given** una búsqueda interrumpida, **When** se vuelve a lanzar con el mismo archivo de estudio, **Then** solo se corren
   los ensayos que faltan hasta el presupuesto.

---

### User Story 2 - Comprobar la mejora en sedes que la búsqueda no vio (Priority: P1)

La mejor cifra de una búsqueda es optimista. El grupo compara, en el 25 % de sedes reservadas, el modelo con parámetros de
partida contra el optimizado, con un intervalo del 95 % que remuestrea sedes completas, y decide con una regla escrita antes.

**Why this priority**: sin esta comprobación no se puede afirmar que optimizar sirvió.

**Independent Test**: con datos hechos a mano, el intervalo remuestrea sedes (una sola sede → intervalo sin ancho) y la
diferencia puntual es exactamente MAE(A) − MAE(B); la reserva no comparte ninguna sede con la búsqueda.

**Acceptance Scenarios**:

1. **Given** el entrenamiento, **When** se reservan sedes, **Then** ~25 % de las sedes quedan reservadas y ninguna está en los
   dos lados.
2. **Given** dos modelos evaluados en la reserva, **When** se calcula la diferencia de MAE, **Then** se obtiene el valor y su
   intervalo del 95 % por sedes; si todo el intervalo está bajo cero, el optimizado gana.

---

### User Story 3 - Dejar cada ensayo registrado (Priority: P2)

Cada ensayo queda como ejecución anidada en MLflow (Databricks, o el respaldo local si no conecta) con sus parámetros, MAE,
RMSE y R² con su desviación entre pliegues, tiempo de ajuste y etiquetas, para poder comparar, reproducir y auditar.

**Why this priority**: lo exige el hito H2 y la guía (sección 4), pero la búsqueda funciona sin él.

**Independent Test**: tras la búsqueda, el experimento tiene una ejecución por ensayo con las métricas indicadas.

### Edge Cases

- Databricks no conecta: se usa MLflow local (`mlflow_local.db`) y el notebook lo avisa.
- Una sede con un solo estudiante: cuenta como una sede completa en la reserva y en el remuestreo.
- Un municipio que solo aparece en la reserva: el preprocesador lo manda a «poco frecuente» (etapa 4).
- Falta `cole_cod_dane_sede`: error claro, nunca una partición por fila.
- Una combinación de parámetros que falla al ajustar: el ensayo se marca como fallido y la búsqueda sigue.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Deben existir espacios de búsqueda para HistGradientBoosting y XGBoost con los rangos de
  `especificaciones/06-optimizacion.md` §4, incluidos `min_frequency` ∈ {0,01; 0,001} y la pérdida (cuadrática o absoluta).
- **FR-002**: La búsqueda minimiza el MAE medio entre pliegues agrupados por sede; registra además RMSE y R² y la
  desviación entre pliegues de las tres.
- **FR-003**: Los parámetros de partida del torneo (umbral 1 %, pérdida cuadrática) se miden con los mismos pliegues de la
  búsqueda y se registran como una ejecución aparte (`<modelo>-partida`): es el «antes» comparable.
- **FR-004**: La búsqueda se guarda en un archivo y se reanuda sin repetir ensayos.
- **FR-005**: Se reserva el 25 % de las sedes del entrenamiento (semilla 7) y se verifica que no comparten sedes con la búsqueda.
- **FR-006**: El intervalo del 95 % de la diferencia de MAE y del MAE de cada modelo remuestrea sedes completas (1.000 veces).
- **FR-007**: Cada ensayo es una ejecución anidada en MLflow con parámetros, métricas y etiquetas `etapa`, `modelo` y
  `metrica_optimizada`.
- **FR-008**: Nada en esta pieza lee `data/processed/test.joblib`.
- **FR-009**: Las reglas de decisión de §6 de la especificación de etapa se escriben en el notebook antes de mostrar resultados.
- **FR-010**: El notebook guarda `reports/06_best_params.json` y `reports/06_comprobacion.csv`; el informe usa solo cifras de
  la ejecución.

### Key Entities

- **Parte de búsqueda / sedes reservadas**: dos subconjuntos del entrenamiento, sin sedes en común.
- **Ensayo**: un conjunto de parámetros con su MAE, RMSE y R² (media y desviación entre pliegues) y su tiempo.
- **Comprobación**: por finalista, MAE de partida y optimizado en la reserva, diferencia e intervalo del 95 % por sedes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La búsqueda completa (25 + 30 ensayos) termina en menos de 30 minutos en el equipo del grupo.
- **SC-002**: El 100 % de los ensayos aparece registrado con sus parámetros y métricas.
- **SC-003**: 0 sedes compartidas entre búsqueda y reserva; 0 lecturas del conjunto de prueba.
- **SC-004**: El informe reporta MAE antes y después y un intervalo del 95 % para cada finalista, y la decisión que sale de la
  regla escrita antes.
- **SC-005**: Todas las pruebas automáticas pasan.

## Assumptions

- Variables base sin variables nuevas y sin escalado (decisiones de las etapas 4 y 5).
- 3 pliegues por sede en la búsqueda (no 5) para caber en el tiempo; por eso el MAE de la búsqueda no es directamente
  comparable con el 33,56 del torneo (5 pliegues sobre todo el entrenamiento). La medición de partida da el «antes» comparable.
- **Desempate entre finalistas (aprobado por el grupo, 5 nov 2026):** si el intervalo de la diferencia entre las dos
  configuraciones elegidas incluye el cero en la reserva, se elige HistGradientBoosting (viene en scikit-learn, sin librerías
  adicionales: simplifica registro y despliegue); si no lo incluye, gana el de menor MAE.
- El archivo del estudio (`optuna_06.db`) no se sube a Git; el registro auditable es MLflow y `reports/`.
