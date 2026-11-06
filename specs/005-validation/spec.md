# Feature Specification: Validación final e interpretación (evaluation.py)

**Feature Branch**: `005-validation` (se trabaja en `main`)

**Created**: 2026-11-05

**Status**: Draft

**Input**: User description: "Etapa 7: entrenar el modelo elegido (HistGradientBoosting optimizado) con todo el
entrenamiento, abrir la prueba una sola vez y medir MAE, RMSE y R² con intervalo por sedes frente a la línea base y la meta;
condición de equidad por estrato, zona, naturaleza y género; importancia por permutación sobre la prueba; completar el
notebook 07 y `reports/07_validacion.md` solo con cifras de la ejecución."

> Fuente de las reglas: `especificaciones/07-validacion.md` (manda sobre esta especificación si hay diferencia).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Medir el modelo final con colegios nunca vistos, una sola vez (Priority: P1)

El grupo necesita saber cuánto se equivoca el modelo elegido con sedes que nunca vio, comparado con no usar modelo (predecir
la mediana) y con las metas (≤ 38 y ≤ 35), con un intervalo honesto.

**Why this priority**: es la cifra que responde si el modelo sirve; sin ella no hay registro ni app.

**Independent Test**: con datos inventados, la diferencia de una métrica entre dos predicciones tiene el valor exacto y su
intervalo remuestrea sedes completas.

**Acceptance Scenarios**:

1. **Given** las decisiones congeladas con fecha, **When** se abre la prueba, **Then** queda una marca con fecha y hora y las
   predicciones se guardan para no volver a evaluar.
2. **Given** las predicciones, **When** se calculan las métricas, **Then** se obtienen MAE, RMSE y R² del modelo y de la línea
   base con intervalos del 95 % por sedes, y la diferencia de cada una.

---

### User Story 2 - Revisar la equidad por segmento (Priority: P1)

El grupo debe comprobar, en cada segmento de estrato (con «Sin Estrato» y vacíos), zona, naturaleza y género, que el modelo
se equivoca menos que la línea base, y decir sin maquillaje dónde no se cumple.

**Why this priority**: es una condición del caso de negocio (`reports/00_caso.md`).

**Independent Test**: con datos hechos a mano, la tabla cuenta bien los estudiantes, calcula el MAE por segmento y marca
«cumple» solo si el modelo es estrictamente mejor.

**Acceptance Scenarios**:

1. **Given** un estudiante con estrato vacío y `sin_estrato` = 1, **When** se asigna su segmento, **Then** es «Sin Estrato»;
   con `sin_estrato` = 0 es «Sin dato (vacío)».
2. **Given** un segmento con igual MAE en modelo y línea base, **When** se evalúa la regla, **Then** no cumple.

---

### User Story 3 - Explicar qué factores pesan (Priority: P2)

El grupo quiere decir en lenguaje simple qué variables mueven más la estimación, con sus límites.

**Independent Test**: con datos inventados, la importancia por permutación es ~0 para una columna que no influye y > 0 para
la que define el objetivo.

### Edge Cases

- Un segmento con muy pocas sedes: el intervalo sale ancho; se informa igual.
- Re-ejecutar el notebook: no vuelve a evaluar con la prueba; reutiliza lo guardado y lo dice.
- `estu_genero` vacío en la prueba: se informa como segmento propio si existe.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Las decisiones (modelo, parámetros, métrica, línea base, metas, regla de equidad) se guardan con fecha y hora
  antes de abrir la prueba.
- **FR-002**: El modelo final se entrena con todo el entrenamiento con los parámetros de `reports/06_best_params.json`.
- **FR-003**: La prueba se abre una vez; queda una marca y las predicciones e importancias se guardan para reutilizarlas.
- **FR-004**: MAE, RMSE y R² del modelo y de la línea base con intervalo del 95 % remuestreando sedes; diferencia de cada
  métrica con su intervalo.
- **FR-005**: Comparación con las metas (≤ 38, ≤ 35), puntual y con el límite superior del intervalo.
- **FR-006**: Tabla de equidad por estrato (8 segmentos), zona, naturaleza y género con estudiantes, sedes, MAE de modelo y
  línea base, diferencia, intervalo y «cumple» (modelo estrictamente menor).
- **FR-007**: Importancia por permutación sobre la prueba con MAE, 5 repeticiones, por columna original usada por el modelo.
- **FR-008**: Nada del modelo se cambia después de abrir la prueba.
- **FR-009**: El informe usa solo cifras de la ejecución y declara los segmentos que no cumplen.

### Key Entities

- **Decisiones congeladas**: modelo, parámetros, métrica, línea base, metas, regla de equidad, fecha y hora.
- **Resultado de prueba**: predicciones del modelo y de la línea base, métricas e intervalos.
- **Segmento**: variable, valor, estudiantes, sedes, MAE modelo, MAE línea base, diferencia, intervalo, cumple.
- **Importancia**: columna, aumento medio del MAE al permutarla, desviación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La prueba se evalúa exactamente una vez (una marca; re-ejecuciones no la reevalúan).
- **SC-002**: El informe trae MAE, RMSE y R² con intervalo, diferencia frente a la línea base y cumplimiento de las dos metas.
- **SC-003**: El 100 % de los segmentos definidos aparece con su veredicto de equidad.
- **SC-004**: Las 21 columnas del modelo tienen su importancia; se explican las principales en lenguaje simple.
- **SC-005**: Todas las pruebas automáticas pasan.

## Assumptions

- No hay calibración ni regla de decisión (regresión).
- La línea base es la mediana del entrenamiento completo (`DummyRegressor`), igual que en el torneo.
- La regla de equidad es la de `reports/00_caso.md` (MAE del modelo menor que el de la línea base en cada segmento); género
  se agrega por pedido del grupo con la misma regla.
- La importancia por permutación se calcula sobre la prueba por pedido del grupo; es interpretación, no se usa para decidir.
