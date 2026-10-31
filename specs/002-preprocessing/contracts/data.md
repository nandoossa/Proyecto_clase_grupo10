# Contrato: `src/proyecto/data/cleaning.py` y `src/proyecto/data/split.py`

## `cleaning.py`

Constantes: `TEST_YEAR = 2022`, `MIN_AGE = 13`, `LEAKAGE_COLUMNS`, `PERSONAL_COLUMNS`, `CONSTANT_COLUMNS`,
`SCHOOL_ID_COLUMNS`, `STRATUM_CODES`, `HOUSEHOLD_SIZE_CODES`, `ROOM_CODES`, `NO_STRATUM = "Sin Estrato"`.

Cada función recibe un `DataFrame` y devuelve uno **nuevo** (no modifica la entrada):

| Función | Regla |
|---|---|
| `drop_exact_duplicates(df)` | 1 |
| `drop_leakage_columns(df)` | 2 |
| `add_age_and_drop_personal(df)` | 3 |
| `mark_impossible_age(df)` | 4 |
| `encode_ordinal_columns(df)` | 7 y 7b (crea `sin_estrato`) |
| `drop_constant_columns(df)` | 8 |
| `drop_school_identifiers(df)` | 9 |
| `keep_calendar_a(df)` | 11 |
| `clean(df)` | todas, en el orden de `research.md` §1 |

Las reglas 6 y 6b no tienen función: `clean` no toca la educación de los padres.

## `split.py`

| Función | Qué hace |
|---|---|
| `split_by_group(df, group_col="cole_cod_dane_sede", test_size=0.2, seed=42)` | `GroupShuffleSplit`; devuelve `(train, test)` con índices reiniciados; llama a `assert_disjoint_groups` |
| `assert_disjoint_groups(*frames, group_col="cole_cod_dane_sede")` | `AssertionError` si una sede aparece en más de una partición |
| `group_cv(n_splits=5)` | `GroupKFold(n_splits)` para validación cruzada agrupada |

Constantes: `GROUP_COL = "cole_cod_dane_sede"`, `RANDOM_STATE = 42`.
