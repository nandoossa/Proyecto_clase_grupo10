---

description: "Lista de tareas: variables y preprocesamiento del modelo (etapa 4)"
---

# Tasks: Variables y preprocesamiento del modelo (etapa 4)

**Input**: Design documents from `/specs/001-feature-engineering/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/engineering.md

**Tests**: se piden explícitamente (`CLAUDE.md`, regla 9, y `especificaciones/04-features.md`, sección 6). Cada prueba se
escribe **antes** que su función y debe fallar primero. Una tarea se marca hecha solo cuando su prueba pasa.

**Organization**: tareas agrupadas por historia de usuario de `spec.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo, sin dependencias pendientes)
- **[Story]**: historia de usuario (US1, US2)

---

## Phase 1: Setup

**Purpose**: dejar listos los archivos de esta pieza.

- [x] T001 Crear `src/proyecto/features/engineering.py` con el docstring del módulo (en español: qué hace, que las variables nuevas quedan apagadas por defecto y que el notebook 04 decide si se encienden) y las importaciones (`numpy`, `pandas`, `ColumnTransformer`, `SimpleImputer`, `Pipeline`, `OneHotEncoder`, `StandardScaler`)
- [x] T002 [P] Crear `tests/test_features.py` con la importación desde `proyecto.features.engineering` y una función auxiliar `_frame(**kw)` que arma una tabla pequeña hecha a mano con todas las columnas de entrada de `data-model.md` (valores inventados para la prueba, nunca filas reales)

---

## Phase 2: Foundational (bloquea las dos historias)

**Purpose**: listas de columnas y la división segura, que usan las dos historias.

- [x] T003 Definir en `src/proyecto/features/engineering.py` las constantes `NUMERIC_BASE` (`edad`, `fami_estratovivienda`, `sin_estrato`, `fami_personashogar`, `fami_cuartoshogar`), `CATEGORICAL_BASE` (las 14 categóricas de `data-model.md`, sin `estu_tipodocumento`, `estu_nacionalidad` ni `estu_privado_libertad`), `MUNICIPALITY_CODES` (`cole_cod_mcpio_ubicacion`, `estu_cod_reside_mcpio`), `NUMERIC_ENGINEERED` (`n_bienes_hogar`, `educacion_max_padres`, `personas_por_cuarto`, `vive_en_mcpio_colegio`) y `FORBIDDEN_COLUMNS` (las 18 de `data-model.md`, incluidas `estu_tipodocumento`, `estu_nacionalidad` y `estu_privado_libertad`)
- [x] T004 Implementar `_ratio(num, den)` en `src/proyecto/features/engineering.py`: «denominador cero o ausente → NaN», como en el ejemplo

**Checkpoint**: constantes y `_ratio` listas.

---

## Phase 3: User Story 1 - Preparar las variables base para cualquier modelo (Priority: P1) 🎯 MVP

**Goal**: `feature_columns` y `build_preprocessor` convierten la tabla limpia en una matriz sin vacíos, sin fuga ni
identificadores, con «sin respuesta», centinelas propios y municipios con «poco frecuente».

**Independent Test**: `pytest tests/test_features.py -k "columns or preprocessor"` en verde.

### Pruebas de US1 (escribir primero; deben fallar)

- [x] T005 [P] [US1] `test_feature_columns_exclude_forbidden` en `tests/test_features.py`: con `use_engineered=True` y `False`, ninguna columna de `FORBIDDEN_COLUMNS` (incluidas `punt_global`, `cole_cod_dane_sede`, `estu_consecutivo`, `estu_tipodocumento`, `estu_nacionalidad` y `estu_privado_libertad`) aparece en numéricas ni categóricas; `extra_numeric=["punt_matematicas"]` lanza `ValueError`
- [x] T006 [P] [US1] `test_feature_columns_toggles` en `tests/test_features.py`: con `use_engineered=False` no aparece ninguna de `NUMERIC_ENGINEERED`; con `True` aparecen las 4; `extra_numeric=["x"]` agrega `x`
- [x] T007 [P] [US1] `test_preprocessor_ignores_forbidden_columns` en `tests/test_features.py`: ajustar `build_preprocessor()` sobre una tabla que **sí** trae `punt_global`, `punt_ingles`, `cole_cod_dane_sede`, `estu_tipodocumento`, `estu_nacionalidad` y `estu_privado_libertad`; ninguna de ellas aparece en `get_feature_names_out()`
- [x] T008 [P] [US1] `test_preprocessor_handles_unseen_category_and_missing` en `tests/test_features.py`: transformar filas con un municipio nunca visto y vacíos en numéricas y categóricas no produce `NaN` ni `inf`
- [x] T009 [P] [US1] `test_sentinels_and_missing_are_separate_categories` en `tests/test_features.py`: con `min_frequency=None` (sin agrupar), «No sabe» y «sin respuesta» de `fami_educacionmadre` quedan en columnas distintas del one-hot
- [x] T010 [P] [US1] `test_numeric_missing_keeps_indicator` en `tests/test_features.py`: con un vacío en `edad` y un estrato vacío con `sin_estrato` = 1 («Sin Estrato»), la salida trae indicadores de vacío para las dos y conserva `sin_estrato`; ningún estrato imputado vale 0

### Implementación de US1

- [x] T011 [US1] Implementar `feature_columns(use_engineered=False, extra_numeric=None)` en `src/proyecto/features/engineering.py`: devuelve `(numéricas, categóricas + MUNICIPALITY_CODES)`; `ValueError` si `extra_numeric` trae una columna de `FORBIDDEN_COLUMNS`
- [x] T012 [US1] Implementar `build_preprocessor(scale=True, use_engineered=False, extra_numeric=None, min_frequency=0.01)` en `src/proyecto/features/engineering.py`: numéricas → `SimpleImputer(strategy="median", add_indicator=True)` + `StandardScaler` si `scale`; categóricas → paso que convierte a texto (los códigos de municipio son enteros) + `SimpleImputer(strategy="constant", fill_value="sin respuesta")` + `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=min_frequency, sparse_output=False)`; `remainder="drop"`
- [x] T013 [US1] Ejecutar `PYTHONUTF8=1 pytest tests/test_features.py` y confirmar T005–T010 en verde

**Checkpoint**: el preprocesador base funciona solo (MVP).

---

## Phase 4: User Story 2 - Probar variables nuevas sin tocar el código (Priority: P2)

**Goal**: `add_features` calcula las 4 variables nuevas sin modificar la tabla original; se encienden con `use_engineered=True`.

**Independent Test**: `pytest tests/test_features.py -k "add_features or ratio or bienes or educacion or cuarto or mcpio"` en verde.

### Pruebas de US2 (escribir primero; deben fallar)

- [x] T014 [P] [US2] `test_add_features_does_not_mutate_input` en `tests/test_features.py`: después de `add_features(frame)`, `frame` no tiene columnas nuevas
- [x] T015 [P] [US2] `test_n_bienes_hogar` en `tests/test_features.py`: computador «Si», internet «Si», automóvil «No», lavadora «No» → 2; las 4 vacías → NaN (no 0)
- [x] T016 [P] [US2] `test_educacion_max_padres` en `tests/test_features.py`: madre «Secundaria (Bachillerato) completa» y padre «No sabe» → 4; ambos «No sabe»/«No Aplica»/vacío → NaN; madre «Primaria completa» y padre «Postgrado» → 9; madre «Técnica o tecnológica completa» y padre «Educación profesional incompleta» → 7 (escala confirmada por el grupo)
- [x] T017 [P] [US2] `test_division_by_zero_or_missing_gives_nan_not_inf` en `tests/test_features.py`: `fami_cuartoshogar=0` o vacío → `personas_por_cuarto` NaN; ninguna columna numérica de la salida tiene `inf`
- [x] T018 [P] [US2] `test_personas_por_cuarto` en `tests/test_features.py`: personas código 2 («3 a 4» → 3,5) y cuartos 2 → 1,75
- [x] T019 [P] [US2] `test_vive_en_mcpio_colegio` en `tests/test_features.py`: códigos iguales → 1; distintos → 0; uno vacío → NaN

### Implementación de US2

- [x] T020 [US2] Definir `PARENT_EDUCATION_LEVELS` (texto → 0–9, escala de `especificaciones/04-features.md`, sección 3) y `HOUSEHOLD_SIZE_MIDPOINTS` (1 → 1,5; 2 → 3,5; 3 → 5,5; 4 → 7,5; 5 → 9) en `src/proyecto/features/engineering.py`
- [x] T021 [US2] Implementar `add_features(df)` en `src/proyecto/features/engineering.py`: trabaja sobre `df.copy()`; calcula `n_bienes_hogar`, `educacion_max_padres`, `personas_por_cuarto` (con `_ratio`) y `vive_en_mcpio_colegio` según `data-model.md`
- [x] T022 [US2] Ejecutar `PYTHONUTF8=1 pytest tests/test_features.py` y confirmar T014–T019 en verde

**Checkpoint**: las dos historias funcionan.

---

## Phase 5: Polish

- [x] T023 Ejecutar toda la suite: `PYTHONUTF8=1 pytest` desde la raíz (sin romper `test_data_load.py`, `test_inference.py`, `test_tracking.py`)
- [ ] T024 [P] Revisar `src/proyecto/features/engineering.py` con el subagente `auditor-de-fuga` y con `material-del-curso/kit/checklist-revision-ia.md`; corregir lo que encuentren
- [x] T025 [P] Marcar en `especificaciones/04-features.md`, sección 6, las casillas de las pruebas que se vieron pasar

---

## Dependencies & Execution Order

- Setup (T001–T002) → Foundational (T003–T004) → US1 (T005–T013) → US2 (T014–T022) → Polish (T023–T025).
- US2 no depende de US1 para sus pruebas, pero `build_preprocessor(use_engineered=True)` necesita que existan las
  columnas de `add_features`; por eso US1 va primero.
- Dentro de cada historia: pruebas → implementación → ejecutar pytest.

### Parallel Opportunities

- T001 y T002 (archivos distintos).
- Todas las pruebas de una misma historia (T005–T010; T014–T019): mismo archivo, pero funciones independientes;
  se pueden escribir juntas.
- T024 y T025.

## Implementation Strategy

1. **MVP = US1**: con `feature_columns` y `build_preprocessor` el torneo (etapa 5) ya puede usar las variables base.
2. **US2**: agrega las variables nuevas apagadas; el notebook 04 decide si se encienden.
3. Fuera de esta lista: `build_pipeline` en `src/proyecto/models/train.py` y la ejecución del notebook 04.
