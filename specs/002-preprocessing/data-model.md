# Data Model: Limpieza y partición (etapa 3)

## Entrada

`data/raw/saber11_antioquia_2022.csv` vía `load_raw_saber11()`: 144.766 filas × 51 columnas (cada estudiante duplicado).

## Salida de `clean(df)`: 72.148 filas × 36 columnas

| Cambio | Columnas | Regla |
|---|---|---|
| Se eliminan (7, fuga) | `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles`, `desemp_ingles`, `estu_estadoinvestigacion` | 2 |
| Se eliminan (2, personales) | `estu_consecutivo`, `estu_fechanacimiento` | 3 |
| Se eliminan (4, constantes) | `periodo`, `cole_cod_depto_ubicacion`, `cole_depto_ubicacion`, `estu_estudiante` | 8 |
| Se eliminan (4, identificadores) | `cole_cod_dane_establecimiento`, `cole_codigo_icfes`, `cole_nombre_establecimiento`, `cole_nombre_sede` | 9 |
| Nueva | `edad`: número; `2022 − año de nacimiento`; vacío si < 13 o fecha ilegible | 3, 4 |
| Nueva | `sin_estrato`: 0/1; 1 solo si el original era «Sin Estrato» | 7b |
| Cambia de texto a número | `fami_estratovivienda`: 1–6; vacío si «Sin Estrato» o vacío | 7, 7b |
| Cambia de texto a número | `fami_personashogar`: `1 a 2` → 1, `3 a 4` → 2, `5 a 6` → 3, `7 a 8` → 4, `9 o más` → 5; vacío → vacío | 7 |
| Cambia de texto a número | `fami_cuartoshogar`: `Uno` → 1 … `Cinco` → 5, `Seis o mas` → 6; vacío → vacío | 7 |
| Sin cambios | `fami_educacionmadre`, `fami_educacionpadre` («No sabe» y «No Aplica» intactos) | 6, 6b |
| Se conservan | `cole_cod_dane_sede` (solo para agrupar), `punt_global` (objetivo) y el resto | — |
| Filas | Se quitan duplicados exactos (72.383) y calendario «OTRO» (235) | 1, 11 |

51 − 7 − 2 − 4 − 4 + 2 = **36 columnas**. Algunas se conservan aunque la etapa 4 no las use como predictores
(`estu_tipodocumento`, `estu_nacionalidad`, `estu_privado_libertad`, nombres de municipio, lugar de presentación,
`cole_calendario`); el preprocesador las ignora (`remainder="drop"` y `FORBIDDEN_COLUMNS`).

## Partición

| Archivo | Contenido |
|---|---|
| `data/processed/train.joblib` | ~80 % de las sedes (todas sus filas) |
| `data/processed/test.joblib` | ~20 % de las sedes; **cerrado hasta la etapa 7** |

Regla: ninguna `cole_cod_dane_sede` en los dos archivos; entrenamiento + prueba = 72.148 filas.

## Compatibilidad con la etapa 4 (`src/proyecto/features/engineering.py`)

| Lo que espera la etapa 4 | Lo que entrega `clean` | ¿Coincide? |
|---|---|---|
| `edad` numérica, vacío posible | `edad` (float; vacío si < 13) | ✅ |
| `fami_estratovivienda` 1–6, vacío, nunca 0 | igual (regla 7b) | ✅ |
| `sin_estrato` 0/1 | igual | ✅ |
| `fami_personashogar` códigos 1–5 (punto medio en `HOUSEHOLD_SIZE_MIDPOINTS`) | 1–5 | ✅ |
| `fami_cuartoshogar` códigos 1–6 | 1–6 | ✅ |
| 14 categóricas (`CATEGORICAL_BASE`) en su texto original | sin cambios | ✅ |
| `fami_educacionmadre/padre` con texto exacto de `PARENT_EDUCATION_LEVELS`, «No sabe», «No Aplica» | sin cambios | ✅ |
| `fami_tiene*` con «Si» / «No» | sin cambios | ✅ |
| `cole_cod_mcpio_ubicacion`, `estu_cod_reside_mcpio` (códigos) | sin cambios | ✅ |
| `cole_cod_dane_sede` para agrupar | se conserva | ✅ |

Una prueba automática (T018 de `tasks.md`) verifica esta tabla.
