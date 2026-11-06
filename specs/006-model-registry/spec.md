# Feature Specification: Registro del modelo, exportación y esquema de entrada

**Feature Branch**: `006-model-registry` (se trabaja en `main`)

**Created**: 2026-11-05

**Status**: Draft

**Input**: User description: "Etapa 8: registrar el modelo evaluado en Unity Catalog como `saber11_puntaje_global` con
parámetros, métricas de la prueba, firma y ejemplo de 21 columnas del entrenamiento y etiquetas de origen; alias champion
con ida y vuelta exacta; exportar `models/model.joblib` desde champion y escribir `models/input_schema.json`; comprobar que
el exportado es el evaluado; adaptar `schema.py` y `predict.py` a regresión con validación; ficha del modelo e informe."

> Fuente de las reglas: `especificaciones/08-registro.md` (manda sobre esta especificación si hay diferencia).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saber qué modelo está en uso y en qué versión (Priority: P1)

El grupo necesita que el modelo evaluado quede registrado con una versión y el alias `champion`, con sus métricas de la
prueba y su origen, y poder recuperarlo idéntico.

**Independent Test**: el modelo recuperado por alias predice exactamente lo mismo que el original.

**Acceptance Scenarios**:

1. **Given** el pipeline evaluado, **When** se registra, **Then** queda una versión con parámetros, métricas, firma de 21
   columnas y etiquetas de origen, y el alias `champion` apunta a ella.
2. **Given** el alias, **When** se carga el modelo, **Then** sus predicciones son idénticas a las del original.

---

### User Story 2 - Un archivo de modelo y un esquema para la app (Priority: P1)

La app (etapa 9) no consulta Databricks: necesita `models/model.joblib` (exportado desde `champion`) y un esquema que diga
qué columnas espera, qué valores son válidos y qué rangos son posibles.

**Independent Test**: el esquema se guarda y se recarga con las 21 columnas; la predicción rechaza entradas imposibles.

**Acceptance Scenarios**:

1. **Given** una fila con una columna faltante, un valor fuera del rango válido o un texto donde va un número, **When** se
   predice, **Then** se rechaza con un mensaje que dice qué corregir.
2. **Given** una fila con vacíos («no sé»), **When** se predice, **Then** devuelve un puntaje.

---

### User Story 3 - Documentar el modelo para quien lo use (Priority: P2)

Ficha del modelo e informe del registro, con cifras de los reportes y los límites declarados.

### Edge Cases

- `final_pipeline.joblib` no existe o su huella no coincide con la de la etapa 7: el notebook se detiene.
- MLflow quedó en local: el notebook se detiene y avisa (el pedido exige Databricks).
- Columnas enteras con vacíos: en la firma se pasan como decimales.
- Un municipio no visto en el entrenamiento: según la decisión del grupo (ver plan).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Registrar el pipeline evaluado como `saber11_puntaje_global` en Unity Catalog, experimento
  `saber11-modelo-final`, con `cloudpickle`.
- **FR-002**: Firma y ejemplo de entrada con exactamente las 21 columnas del modelo, tomados del entrenamiento.
- **FR-003**: Métricas de la prueba (MAE, RMSE, R² con intervalos) y de la línea base; etiquetas de etapa, fecha y commit.
- **FR-004**: Alias `champion` y comprobación de ida y vuelta con igualdad exacta.
- **FR-005**: Exportar `models/model.joblib` desde `champion`; escribir `models/input_schema.json` solo con el entrenamiento.
- **FR-006**: Comprobar que el exportado es el evaluado, sin volver a evaluar con la prueba (forma a decidir por el grupo).
- **FR-007**: Predicción de regresión que valida contra el esquema y rechaza faltantes, no numéricos y fuera de rango.
- **FR-008**: La mediana del esquema sale solo del entrenamiento y nunca se calcula al predecir.
- **FR-009**: Ficha e informe con cifras de los reportes; sin correos, direcciones del espacio de trabajo ni tokens.

### Key Entities

- **Versión registrada**: nombre completo, número, alias, ejecución, etiquetas.
- **Esquema de entrada**: columnas, tipos, categorías válidas, rangos observados y válidos, medianas.

## Success Criteria *(mandatory)*

- **SC-001**: Una versión registrada con alias `champion` y ida y vuelta exacta.
- **SC-002**: `model.joblib` y `input_schema.json` en el repositorio, con 21 columnas.
- **SC-003**: Evidencia de que el exportado es el evaluado y de que el MAE de la prueba es 33,316.
- **SC-004**: El 100 % de las entradas imposibles de prueba se rechazan con un mensaje claro.
- **SC-005**: Todas las pruebas automáticas pasan; 0 datos sensibles en lo que se sube.

## Assumptions

- `registered_model_name` usa `UC_CATALOG` y `UC_SCHEMA` de `.env` (por defecto `workspace.default`).
- Los rangos válidos de la especificación de etapa (§3) son conocimiento del grupo, a confirmar.
- Las funciones de clasificación de la plantilla se conservan hasta la etapa 9 para no romper la app de plantilla.
