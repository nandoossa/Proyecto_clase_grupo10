# Feature Specification: Limpieza y partición de los datos (etapa 3)

**Feature Branch**: `002-preprocessing` (se trabaja en `main`, como el resto del repositorio)

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Etapa 3 · Preprocesamiento según `especificaciones/03-preprocesamiento.md` (cerrada): limpieza
(`cleaning.py`), partición por sede (`split.py`) y `notebooks/03_preprocesamiento.ipynb`. La salida debe coincidir con lo que
espera `src/proyecto/features/engineering.py`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Limpiar los datos con las decisiones aprobadas (Priority: P1)

El grupo necesita convertir el archivo original de Saber 11 (144.766 filas) en una tabla limpia: sin duplicados, sin
columnas con fuga, sin datos personales, con la edad y las categorías ordenadas como números, y solo con estudiantes de
calendario A, aplicando exactamente las reglas aprobadas y sin modificar el archivo original.

**Why this priority**: sin datos limpios no hay partición, ni variables (etapa 4), ni modelo.

**Independent Test**: con tablas pequeñas hechas a mano, cada regla produce el resultado esperado. Con los datos reales,
la tabla limpia tiene 72.148 filas y ninguna columna prohibida.

**Acceptance Scenarios**:

1. **Given** dos filas idénticas, **When** se limpia, **Then** queda una.
2. **Given** un estudiante nacido en 2015, **When** se limpia, **Then** su edad queda vacía y la fila se conserva.
3. **Given** un estudiante con «Sin Estrato», **When** se limpia, **Then** su estrato queda vacío (nunca 0) y `sin_estrato` = 1.
4. **Given** un estudiante de calendario «OTRO», **When** se limpia, **Then** su fila no aparece.
5. **Given** la tabla limpia, **When** se buscan `estu_consecutivo`, `estu_fechanacimiento` o las 7 columnas con fuga,
   **Then** no están.

---

### User Story 2 - Partir por sede sin mezclar colegios (Priority: P1)

El grupo necesita separar el 20 % de las sedes como prueba cerrada, de modo que ningún colegio-sede aparezca en
entrenamiento y prueba a la vez.

**Why this priority**: es la condición para que el MAE mida el error con colegios no vistos, como en la app (decisión 10).

**Independent Test**: con una tabla hecha a mano de muchas sedes, ninguna sede cae a los dos lados, no se pierde ninguna
fila y una partición por fila sería detectada.

**Acceptance Scenarios**:

1. **Given** la tabla limpia, **When** se parte, **Then** ninguna sede está en entrenamiento y prueba a la vez.
2. **Given** la tabla limpia, **When** se parte, **Then** entrenamiento + prueba = todas las filas.
3. **Given** una partición mezclada a propósito, **When** se verifica, **Then** la verificación falla.

---

### User Story 3 - Regenerar todo desde cero con el notebook 03 (Priority: P2)

El grupo necesita un notebook que, con `data/processed/` borrada, cargue los datos, limpie, verifique, parta y guarde
`train.joblib` y `test.joblib`, sin pasos manuales.

**Why this priority**: es criterio de cierre del hito H1; las etapas siguientes leen `data/processed/train.joblib`.

**Independent Test**: borrar `data/processed/`, ejecutar el notebook de principio a fin y comprobar que los dos archivos
existen y que las comprobaciones pasan.

**Acceptance Scenarios**:

1. **Given** `data/processed/` vacía, **When** se ejecuta el notebook, **Then** se crean `train.joblib` y `test.joblib`.
2. **Given** la tabla limpia, **When** se pasa por `add_features` y `build_preprocessor` de la etapa 4, **Then** funciona
   sin errores (las columnas coinciden).

### Edge Cases

- Fecha de nacimiento vacía o ilegible: edad vacía (hoy no hay ninguna en los datos, pero la regla debe soportarlo).
- Estrato vacío real frente a «Sin Estrato»: los dos dan estrato vacío; solo «Sin Estrato» tiene `sin_estrato` = 1.
- Una sede con un solo estudiante: va completa a un lado.
- El archivo de entrada no debe cambiar al limpiar (la limpieza trabaja sobre copias).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST aplicar las reglas 1, 2, 3, 4, 6, 6b, 7, 7b, 8, 9 y 11 de
  `especificaciones/03-preprocesamiento.md`, sección 3, exactamente como están escritas.
- **FR-002**: El sistema MUST quitar los duplicados exactos **antes** de eliminar `estu_consecutivo`.
- **FR-003**: El sistema MUST calcular `edad = 2022 − año de nacimiento` y eliminar luego `estu_consecutivo` y
  `estu_fechanacimiento`.
- **FR-004**: El sistema MUST marcar como vacía la edad menor de 13 y conservar la fila.
- **FR-005**: El sistema MUST codificar estrato (1–6, «Sin Estrato» → vacío y `sin_estrato` = 1), personas (1–5) y cuartos
  (1–6), dejando vacío lo vacío.
- **FR-006**: El sistema MUST NOT tocar «No sabe» ni «No Aplica» en la educación de los padres.
- **FR-007**: El sistema MUST conservar `cole_cod_dane_sede`, `punt_global` y las columnas que usa la etapa 4.
- **FR-008**: El sistema MUST partir 20 % de prueba por `cole_cod_dane_sede` con `GroupShuffleSplit`, semilla 42.
- **FR-009**: El sistema MUST ofrecer validación cruzada agrupada por sede (`GroupKFold`) para las etapas siguientes.
- **FR-010**: El sistema MUST NOT modificar `data/raw/` y MUST guardar la salida en `data/processed/`, que no se sube a
  GitHub.
- **FR-011**: El notebook 03 MUST solo orquestar: llama a funciones de `src/proyecto/data/`.

### Key Entities

- **Estudiante (fila)**: un estudiante de calendario A, Antioquia, periodo 20224; 72.148 tras limpiar.
- **Sede (`cole_cod_dane_sede`)**: 1.447 en los datos sin duplicados; unidad de partición.
- **Partición**: entrenamiento (~80 % de las sedes) y prueba cerrada (~20 %), guardadas en `data/processed/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las pruebas automáticas de la etapa pasan.
- **SC-002**: 0 sedes compartidas entre entrenamiento y prueba; 0 filas perdidas en la partición.
- **SC-003**: La tabla limpia tiene 72.148 filas, 0 columnas personales y 0 columnas con fuga.
- **SC-004**: El notebook 03 regenera `data/processed/` desde cero sin pasos manuales.
- **SC-005**: La tabla limpia funciona con el preprocesador de la etapa 4 sin errores.

## Assumptions

- Año de la prueba: 2022 (periodo 20224). La edad es aproximada (no considera mes ni día), como dice el EDA.
- El 20 % se aplica a las **sedes**; el porcentaje de filas en prueba será cercano a 20 %, pero no exacto.
- `data/processed/` hoy no está en `.gitignore`; se agrega para que la salida no se suba (el notebook dice que «no se
  versiona», y la licencia CC BY-SA pide publicar con la misma licencia cualquier versión modificada de los datos).
- Fuera de alcance: imputación y codificación (etapa 4), `build_pipeline` y el modelado.
