---

description: "Lista de tareas: limpieza y partición de los datos (etapa 3)"
---

# Tasks: Limpieza y partición de los datos (etapa 3)

**Input**: Design documents from `/specs/002-preprocessing/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/data.md

**Tests**: se piden explícitamente (`CLAUDE.md`, regla 9; `especificaciones/03-preprocesamiento.md`, sección 6). Cada prueba
se escribe **antes** que su función y debe fallar primero. Una tarea se marca hecha solo cuando su prueba pasa.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo, sin dependencias pendientes)
- **[Story]**: US1 limpieza, US2 partición, US3 notebook

---

## Phase 1: Setup

- [ ] T001 Agregar `data/processed/*` y `!data/processed/.gitkeep` a `.gitignore` y crear `data/processed/.gitkeep`
- [ ] T002 [P] Crear `src/proyecto/data/cleaning.py` con docstring del módulo (en español) y las constantes de `contracts/data.md`: `TEST_YEAR = 2022`, `MIN_AGE = 13`, `LEAKAGE_COLUMNS` (las 7), `PERSONAL_COLUMNS` (`estu_consecutivo`, `estu_fechanacimiento`), `CONSTANT_COLUMNS` (las 4), `SCHOOL_ID_COLUMNS` (las 4), `STRATUM_CODES` (`Estrato 1`…`Estrato 6` → 1…6), `HOUSEHOLD_SIZE_CODES` (`1 a 2` → 1 … `9 o más` → 5), `ROOM_CODES` (`Uno` → 1 … `Seis o mas` → 6), `NO_STRATUM = "Sin Estrato"`
- [ ] T003 [P] Crear `src/proyecto/data/split.py` con docstring y `GROUP_COL = "cole_cod_dane_sede"`, `RANDOM_STATE = 42`
- [ ] T004 [P] Crear `tests/test_cleaning.py` y `tests/test_split.py` con sus importaciones y una función `_raw(**kw)` que arma filas hechas a mano con el formato del CSV crudo (valores inventados, nunca filas reales)

---

## Phase 2: User Story 1 - Limpiar los datos con las decisiones aprobadas (Priority: P1) 🎯 MVP

**Goal**: `clean(df)` aplica las reglas 1, 2, 3, 4, 6, 6b, 7, 7b, 8, 9 y 11.

**Independent Test**: `PYTHONUTF8=1 python -m pytest tests/test_cleaning.py` en verde.

### Pruebas de US1 (escribir primero; deben fallar)

- [ ] T005 [P] [US1] `test_drop_exact_duplicates`: dos filas idénticas → una; dos filas que solo difieren en `estu_consecutivo` → se conservan las dos
- [ ] T006 [P] [US1] `test_drop_leakage_columns`: las 7 columnas desaparecen y `punt_global` se conserva
- [ ] T007 [P] [US1] `test_no_personal_columns`: tras `clean`, no existen `estu_consecutivo` ni `estu_fechanacimiento`; `edad` de «14/01/2001» = 21; fecha ilegible → vacío
- [ ] T008 [P] [US1] `test_mark_impossible_age`: edad 12 → vacío (fila conservada); 13 y 80 se conservan
- [ ] T009 [P] [US1] `test_encode_ordinal_columns`: personas `9 o más` → 5, cuartos `Seis o mas` → 6, `Estrato 4` → 4, vacío → vacío; un texto no previsto → vacío
- [ ] T010 [P] [US1] `test_sin_estrato_flag`: «Sin Estrato» → estrato vacío (no 0) y `sin_estrato` = 1; vacío real → estrato vacío y `sin_estrato` = 0; `Estrato 2` → 2 y `sin_estrato` = 0
- [ ] T011 [P] [US1] `test_sentinels_are_kept`: «No sabe» y «No Aplica» en `fami_educacionmadre` y `fami_educacionpadre` llegan intactos después de `clean`
- [ ] T012 [P] [US1] `test_drop_constant_columns` y `test_drop_school_identifiers`: desaparecen las 4 + 4 columnas; `cole_cod_dane_sede` se conserva
- [ ] T013 [P] [US1] `test_keep_calendar_a`: filas con `cole_calendario == "OTRO"` desaparecen; las de «A» se conservan
- [ ] T014 [P] [US1] `test_clean_does_not_mutate_input`: la tabla de entrada queda igual después de `clean`

### Implementación de US1

- [ ] T015 [US1] Implementar en `src/proyecto/data/cleaning.py` `drop_exact_duplicates`, `drop_leakage_columns`, `add_age_and_drop_personal` (`pd.to_datetime(format="%d/%m/%Y", errors="coerce")`, `edad = TEST_YEAR − año`), `mark_impossible_age` (`edad < MIN_AGE` → NaN), `encode_ordinal_columns` (diccionarios de T002; crea `sin_estrato` = 1 solo si el valor original es `NO_STRATUM`), `drop_constant_columns`, `drop_school_identifiers`, `keep_calendar_a`; cada una sobre una copia
- [ ] T016 [US1] Implementar `clean(df)` en `src/proyecto/data/cleaning.py` en el orden de `research.md` §1 (duplicados primero)
- [ ] T017 [US1] Ejecutar `PYTHONUTF8=1 python -m pytest tests/test_cleaning.py` y confirmar T005–T014 en verde

### Compatibilidad con la etapa 4

- [ ] T018 [US1] `test_clean_output_matches_feature_stage` en `tests/test_cleaning.py`: `clean(_raw())` contiene todas las columnas de `feature_columns(use_engineered=False)` y `cole_cod_dane_sede`; `fami_personashogar` ⊆ {1..5}, `fami_cuartoshogar` ⊆ {1..6}, `fami_estratovivienda` ⊆ {1..6} o vacío; `build_preprocessor(use_engineered=True).fit_transform(add_features(clean(_raw())))` no da error ni vacíos. Confirmar en verde

**Checkpoint**: limpieza completa y compatible con la etapa 4.

---

## Phase 3: User Story 2 - Partir por sede sin mezclar colegios (Priority: P1)

**Goal**: `split_by_group`, `assert_disjoint_groups` y `group_cv` en `src/proyecto/data/split.py`.

**Independent Test**: `PYTHONUTF8=1 python -m pytest tests/test_split.py` en verde.

### Pruebas de US2 (escribir primero; deben fallar)

- [ ] T019 [P] [US2] `test_split_never_shares_a_school_between_train_and_test`: tabla de ~200 sedes con varios estudiantes cada una; ninguna sede a los dos lados; train + test = todas las filas
- [ ] T020 [P] [US2] `test_split_keeps_each_school_together`: cada sede tiene todos sus estudiantes en un solo lado
- [ ] T021 [P] [US2] `test_assert_disjoint_raises_on_overlap`: dos partes que comparten una sede → `AssertionError`
- [ ] T022 [P] [US2] `test_row_split_would_share_schools`: una partición por fila (`train_test_split`) de la misma tabla sí comparte sedes y `assert_disjoint_groups` la rechaza (demuestra por qué se parte por sede)
- [ ] T023 [P] [US2] `test_group_cv_folds_do_not_share_schools`: en cada pliegue de `group_cv(5)`, ninguna sede está en entrenamiento y validación a la vez
- [ ] T024 [P] [US2] `test_split_is_reproducible`: misma semilla → misma partición; `test_size=0.2` deja entre 10 % y 30 % de las filas en prueba

### Implementación de US2

- [ ] T025 [US2] Implementar `split_by_group(df, group_col=GROUP_COL, test_size=0.2, seed=RANDOM_STATE)`, `assert_disjoint_groups(*frames, group_col=GROUP_COL)` y `group_cv(n_splits=5)` (`GroupKFold`) en `src/proyecto/data/split.py`, como en `contracts/data.md`
- [ ] T026 [US2] Ejecutar `PYTHONUTF8=1 python -m pytest tests/test_split.py` y confirmar T019–T024 en verde

**Checkpoint**: partición por sede verificada.

---

## Phase 4: User Story 3 - Regenerar todo desde cero con el notebook 03 (Priority: P2)

**Goal**: `notebooks/03_preprocesamiento.ipynb` solo orquesta y regenera `data/processed/`.

**Independent Test**: borrar `data/processed/*.joblib`, ejecutar el notebook completo y comprobar los dos archivos.

- [ ] T027 [US3] En `notebooks/03_preprocesamiento.ipynb`, sección 0: cargar con `load_raw_saber11(RAW_DIR)` en vez de buscar cualquier archivo; `ID_COL = "cole_cod_dane_sede"`, `TARGET = "punt_global"`; no mostrar filas antes de limpiar (datos personales)
- [ ] T028 [US3] Sección 2 del notebook: reemplazar «no se perdieron filas» por comprobaciones de las reglas: 72.148 filas, 36 columnas, sin columnas personales ni con fuga, `sin_estrato` solo 0/1, códigos de personas 1–5 y cuartos 1–6, `edad` mínima ≥ 13 o vacía, solo calendario «A»
- [ ] T029 [US3] Sección 3 del notebook: `split_by_group(clean_df, group_col=ID_COL, test_size=0.2, seed=42)`; escribir el texto «Mi unidad de análisis y por qué parto así» con lo que dice `especificaciones/03-preprocesamiento.md`, sección 1
- [ ] T030 [US3] Borrar `data/processed/*.joblib` (si existen) y ejecutar el notebook de principio a fin; anotar las filas de entrenamiento y prueba que salen (sin mirar el contenido de la prueba)
- [ ] T031 [US3] Comprobar con `git status` que `data/raw/` y `data/processed/` no aparecen y que `data/raw/saber11_antioquia_2022.csv` no cambió

---

## Phase 5: Polish

- [ ] T032 Ejecutar `PYTHONUTF8=1 python -m pytest tests` (todas las del proyecto) en verde
- [ ] T033 [P] Corregir la sección 5 de `especificaciones/03-preprocesamiento.md` (`train.joblib` / `test.joblib`) si el grupo aprueba el formato, y marcar en sus secciones 6 y 7 lo que se vio funcionando
- [ ] T034 [P] Revisar `src/proyecto/data/` y el notebook 03 con el subagente `auditor-de-fuga` (que lea la constitución y `03-preprocesamiento.md`) y con `material-del-curso/kit/checklist-revision-ia.md`

---

## Dependencies & Execution Order

- Setup (T001–T004) → US1 (T005–T018) y US2 (T019–T026) en paralelo (archivos distintos) → US3 (T027–T031, necesita las
  dos) → Polish (T032–T034).
- Dentro de cada historia: pruebas → implementación → pytest.

### Parallel Opportunities

- T002, T003 y T004.
- US1 y US2 completas (cleaning y split son independientes).
- Las pruebas de cada historia entre sí.

## Implementation Strategy

1. **MVP = US1 + US2**: con `clean` y `split_by_group` probados ya se puede regenerar la partición.
2. **US3**: el notebook la deja reproducible y produce `data/processed/train.joblib`, que necesita el notebook 04.
3. Fuera de esta lista: `build_pipeline` (`src/proyecto/models/train.py`) y la corrección de las pruebas de la etapa 4 que
   señaló `reports/auditoria_etapa4.md` (el grupo decide).
