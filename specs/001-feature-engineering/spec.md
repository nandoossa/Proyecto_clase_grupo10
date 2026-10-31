# Feature Specification: Variables y preprocesamiento del modelo (etapa 4)

**Feature Branch**: `001-feature-engineering` (se trabaja en `main`, como el resto del repositorio)

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Etapa 4 · Variables y preprocesamiento del modelo, según `especificaciones/04-features.md`:
columnas base `cole_`/`estu_`/`fami_` sin fuga ni identificadores, 4 variables nuevas candidatas apagadas por defecto,
preprocesamiento con «sin respuesta», centinelas como categorías propias y municipios con agrupación de poco frecuentes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preparar las variables base para cualquier modelo (Priority: P1)

El grupo necesita convertir la tabla limpia de estudiantes (salida de la etapa 3) en una tabla numérica que cualquier
modelo pueda usar, con solo información que se conoce antes del examen, tratando los vacíos y las categorías especiales
como se decidió en el EDA.

**Why this priority**: sin esto no se puede entrenar ningún modelo en el torneo (etapa 5) ni medir el MAE frente a la
línea base de 42,8 puntos.

**Independent Test**: con una tabla pequeña hecha a mano que imita la salida de la etapa 3, el preprocesamiento ajustado
produce una tabla sin vacíos, sin columnas con fuga ni identificadores, y con «No sabe» y «sin respuesta» como columnas
distintas.

**Acceptance Scenarios**:

1. **Given** una tabla limpia con vacíos en `fami_` y en `cole_bilingue`, **When** se ajusta y aplica el preprocesamiento,
   **Then** la salida no tiene vacíos y el vacío queda registrado (categoría «sin respuesta» o indicador de vacío).
2. **Given** una tabla que contiene por error una columna con fuga o un identificador, **When** se obtiene la lista de
   columnas del modelo, **Then** ninguna de esas columnas está en la lista.
3. **Given** un estudiante de un municipio que no apareció en entrenamiento, **When** se transforma, **Then** no hay error
   y el municipio cae en el grupo «poco frecuente».

---

### User Story 2 - Probar variables nuevas sin tocar el código (Priority: P2)

El grupo quiere comprobar si cuatro variables nuevas (bienes del hogar, educación más alta de los padres, personas por
cuarto y si vive en el municipio del colegio) bajan el MAE, encendiéndolas o apagándolas con un interruptor.

**Why this priority**: es el experimento del notebook 04; si no mejoran el MAE, el modelo final funciona sin ellas.

**Independent Test**: con filas hechas a mano se comprueba el valor de cada variable nueva, que la tabla original no
cambia y que una división por cero da vacío y no infinito.

**Acceptance Scenarios**:

1. **Given** un hogar con computador e internet pero sin automóvil ni lavadora, **When** se calculan las variables nuevas,
   **Then** `n_bienes_hogar` vale 2.
2. **Given** madre con secundaria completa y padre «No sabe», **When** se calculan, **Then** `educacion_max_padres` vale 4.
3. **Given** un hogar con 0 cuartos o sin dato de personas, **When** se calculan, **Then** `personas_por_cuarto` queda vacía.
4. **Given** el interruptor de variables nuevas apagado, **When** se pide la lista de columnas, **Then** no aparece ninguna
   de las cuatro.

---

### Edge Cases

- Estudiante que no respondió ninguna pregunta de bienes (2,6 %): `n_bienes_hogar` vacía, no 0.
- Ambos padres con «No sabe», «No Aplica» o vacío: `educacion_max_padres` vacía.
- Edad marcada como vacía por ser menor de 13 años (etapa 3): se imputa y queda el indicador de vacío.
- Categoría nunca vista o vacía en la app: no produce error ni vacíos en la salida.
- «Sin Estrato»: llega con estrato vacío y `sin_estrato` = 1; se imputa el estrato y queda el indicador de vacío.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST usar como predictores solo las columnas base listadas en `especificaciones/04-features.md`
  (sección 2): 5 numéricas, 16 categóricas y 2 códigos de municipio.
- **FR-002**: El sistema MUST excluir siempre `punt_global`, las 7 columnas con fuga, `estu_consecutivo`,
  `estu_fechanacimiento`, `cole_cod_dane_sede`, los demás identificadores del colegio y `estu_tipodocumento` (excluida
  por el grupo por equidad), aunque estén en la tabla de entrada.
- **FR-003**: El sistema MUST calcular las 4 variables nuevas con las reglas exactas de la sección 3 de
  `especificaciones/04-features.md`, sin modificar la tabla original.
- **FR-004**: Toda división por cero o con datos faltantes MUST dar vacío, nunca infinito.
- **FR-005**: Las variables nuevas MUST estar apagadas por defecto y encenderse con un interruptor.
- **FR-006**: Los vacíos de categóricas MUST convertirse en la categoría «sin respuesta» (decisión 5 del EDA).
- **FR-007**: Los vacíos de numéricas MUST imputarse con un valor aprendido solo del entrenamiento y conservar un
  indicador de que estaban vacíos.
- **FR-008**: «No sabe», «No Aplica» y «Sin Estrato» MUST quedar como categorías propias (decisión 6 del EDA).
- **FR-009**: Las categorías con menos del 1 % de los estudiantes, y las nunca vistas, MUST agruparse en «poco frecuente»;
  el umbral MUST ser configurable.
- **FR-010**: Todo lo que aprende de los datos (imputación, escala, categorías) MUST ajustarse solo con entrenamiento.
- **FR-011**: El escalado de numéricas MUST poder apagarse (para modelos de árboles).

### Key Entities

- **Estudiante (fila)**: un estudiante de calendario A en Antioquia, periodo 20224, con atributos del colegio, propios y
  de la familia; objetivo `punt_global`.
- **Sede (`cole_cod_dane_sede`)**: agrupa estudiantes; solo se usa para partir y validar, nunca como predictor.
- **Variable nueva**: columna derivada de otras columnas de la misma fila, apagada por defecto.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las pruebas automáticas de esta etapa pasan.
- **SC-002**: 0 columnas con fuga o identificadores en la lista de predictores, verificado por una prueba.
- **SC-003**: Transformar filas con categorías nuevas y vacíos produce 0 vacíos y 0 infinitos en la salida.
- **SC-004**: El notebook 04 reporta el MAE con y sin variables nuevas sobre los mismos 5 pliegues agrupados por sede, y la
  decisión queda escrita con su cifra.

## Assumptions

- La etapa 3 entrega `edad`, `sin_estrato` y las versiones numéricas de estrato, personas y cuartos, según
  `especificaciones/03-preprocesamiento.md`. «Sin Estrato» (opción A, regla 7b): estrato vacío, nunca 0, y
  `sin_estrato` = 1. **Aprobado por el grupo el 31 oct 2026.**
- Escala de `educacion_max_padres` (técnica completa = 6, profesional incompleta = 7); «No sabe» y «No Aplica» fuera de
  la escala. **Confirmada por el grupo el 31 oct 2026.**
- `estu_tipodocumento` no es predictor (grupo, 31 oct 2026): repite la edad y señalaría la condición migratoria.
- Umbral de poco frecuentes: 1 %. El notebook 04 puede probar otro umbral o codificación por objetivo.
- Fuera de alcance: `build_pipeline` (unión con el modelo) y la ejecución del notebook 04.
