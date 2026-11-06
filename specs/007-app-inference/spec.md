# Feature Specification: Inferencia de regresión y app de Streamlit (etapa 9)

**Feature Branch**: `007-app-inference` (se trabaja en `main`)

**Created**: 2026-11-06

**Status**: Draft

**Input**: pedido del grupo del 6 nov 2026 y `especificaciones/09-app.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Estimar el puntaje de un estudiante desde un formulario (Priority: P1)

Una persona (Secretaría, rector, docente, estudiante o familia) llena un formulario en español con los datos del colegio,
del estudiante y del hogar, y recibe el puntaje global estimado, redondeado, con el error típico del modelo y el aviso de
uso responsable.

**Why this priority**: es el producto de la startup; sin esto no hay demo en la clase 5.

**Independent Test**: con AppTest, llenar un perfil normal y comprobar que aparece un puntaje entero, el error típico y el
aviso.

**Acceptance Scenarios**:

1. **Given** un perfil completo y válido, **When** se pulsa «Estimar», **Then** aparece un puntaje entero entre 100 y 477 y
   el texto del error típico (±33 puntos, MAE 33,3).
2. **Given** «Sin respuesta» en los campos que lo admiten, **When** se pulsa «Estimar», **Then** también aparece un puntaje.
3. **Given** cualquier estado de la app, **Then** el aviso de uso responsable está visible, con estrato 5 (MAE 39,57) y la
   brecha por género (35,74 frente a 31,40).

---

### User Story 2 - Rechazar entradas inválidas con un mensaje de corrección (Priority: P1)

Si un dato es imposible o falta uno obligatorio, la app no da un puntaje: dice qué corregir.

**Why this priority**: un modelo que contesta cualquier cosa es más peligroso que uno que dice «no» (guía, sección 7).

**Independent Test**: con AppTest, edad 12 (o «abc») y un campo obligatorio vacío.

**Acceptance Scenarios**:

1. **Given** una edad fuera de 13–80 o que no es un número entero, **When** se pulsa «Estimar», **Then** se ve un mensaje
   que nombra la edad y **no** se ve ningún puntaje.
2. **Given** un campo obligatorio sin elegir, **When** se pulsa «Estimar», **Then** el mensaje nombra ese campo.

---

### User Story 3 - Inferencia solo de regresión y notebook de ejemplo (Priority: P2)

`predict.py` queda con solo la regresión, y el notebook 09 muestra 3–4 perfiles inventados y un rechazo, sin Databricks ni
la prueba.

**Independent Test**: `pytest`; ejecutar el notebook 09 de principio a fin.

### Edge Cases

- Municipio con un código no visto: advertencia, no error.
- «Sin estrato» frente a «Sin respuesta» en el estrato: el primero da `sin_estrato` = 1; el segundo, estrato vacío y
  `sin_estrato` = 0 (regla 7b de la etapa 3).
- Faltan `models/model.joblib` o `models/input_schema.json`: la app muestra un error claro y se detiene.

## Requirements *(mandatory)*

- **FR-001**: `predict.py` MUST conservar solo `InputValidationError`, `load_model`, `validate_inputs` y `predict_score`.
- **FR-002**: La app MUST cargar solo `models/model.joblib` y `models/input_schema.json`, sin `mlflow` ni `databricks`.
- **FR-003**: La app MUST traducir el formulario (texto) a las 21 columnas del esquema, con los códigos de la etapa 3.
- **FR-004**: La app MUST ofrecer «Sin respuesta» solo en los campos `nullable` del esquema.
- **FR-005**: La app MUST rechazar con un mensaje de corrección las entradas inválidas, sin mostrar una estimación.
- **FR-006**: La app MUST mostrar el puntaje redondeado a entero y el error típico (MAE 33,3 de la prueba).
- **FR-007**: La app MUST mostrar siempre el aviso de uso responsable con los límites de la ficha.
- **FR-008**: El notebook 09 MUST usar perfiles inventados y no abrir la prueba.

## Success Criteria *(mandatory)*

- **SC-001**: `pytest` en verde, con las pruebas de AppTest.
- **SC-002**: `streamlit run app/streamlit_app.py` abre la app en local y responde los 4 casos de `reports/09_despliegue.md`.
- **SC-003**: La auditoría de la etapa 9 no encuentra fuga ni datos sensibles.

## Assumptions

- El modelo y el esquema de la etapa 8 no cambian (salvo claves de presentación en el esquema, si el grupo aprueba P2).
- El género sigue como entrada porque el modelo lo usa; quitarlo exigiría reentrenar (fuera de esta etapa).
- No se despliega en esta etapa: `reports/09_despliegue.md` se llena con el plan de despliegue y el plan B.
