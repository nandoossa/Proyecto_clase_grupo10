# Especificación · Etapa 3 · Preprocesamiento (limpieza y partición)

> Se llena **antes** de pedirle código a Claude, a partir de la tabla de decisiones de
> `especificaciones/02-eda.md`. Claude la lee y la implementa; ustedes revisan que el código haga
> **exactamente** esto (`material-del-curso/kit/checklist-revision-ia.md`).
> Guía: `material-del-curso/kit/guia-eda-y-preprocesamiento.md`, sección 4 · Ejemplo: `material-del-curso/ejemplo-creditsight/src/creditsight/data/`.

**Grupo:** Predictor de resultados Pruebas Saber 11 en Antioquia   **Fecha:** 31 oct 2026   **Estado:** ☐ borrador  ☒ cerrada

> Preparada por Claude a partir de `reports/01_eda.md` (decisiones aprobadas por el grupo el 31 oct 2026) y de los datos
> de `data/raw/`. Los puntos abiertos los decidió el grupo el 31 oct 2026.

## 1. Unidad de análisis y partición

- **Una fila es:** un estudiante que presentó Saber 11 en el periodo 20224 en un colegio de Antioquia (72.383 filas tras
  quitar duplicados exactos).
- **Entidad que se repite (columna):** `cole_cod_dane_sede` (sede del colegio: 1.447 sedes, mediana de 33 estudiantes por
  sede; explica el 36 % de la variación del puntaje). El estudiante no se repite tras quitar duplicados.
- **Se parte por:** ☒ grupo (`GroupShuffleSplit` para entrenamiento/prueba; `GroupKFold` para validación cruzada, porque es
  regresión y no hay clases que estratificar) ☐ fila
- **Proporción de prueba:** 20 %, partida por sede (`cole_cod_dane_sede`) con `GroupShuffleSplit` (grupo, 31 oct 2026)   **Semilla:** 42
- **¿Hay orden temporal que respetar?** ☒ no ☐ sí → un solo periodo (20224).
- **Función de partición:** `split_by_group(df, group_col, test_size, seed)` en `src/proyecto/data/split.py` (grupo,
  31 oct 2026). Motivo: es el nombre que usa la plantilla de `notebooks/03_preprocesamiento.ipynb`.
- **Dónde se guarda la prueba:** `data/processed/test.joblib` (cerrada: **no se mira** hasta la etapa 7)

## 2. Datos personales

| Columna | Qué es | Se elimina en | Prueba que lo verifica |
|---|---|---|---|
| `estu_consecutivo` | Identificador del estudiante | Después de quitar duplicados (decisión 1): se usa solo para eso | `test_no_personal_columns` |
| `estu_fechanacimiento` | Fecha de nacimiento (formato `dd/mm/aaaa`) | Después de calcular la edad (decisión 3) | `test_no_personal_columns` |

> `load_raw_saber11()` (ya existe en `src/proyecto/data/load.py`) devuelve el archivo **tal cual**; las columnas
> personales se quitan en el primer paso de limpieza, en este orden: duplicados → edad → eliminar las dos columnas.
> Quitar `estu_consecutivo` **antes** de los duplicados podría juntar a dos estudiantes distintos con las mismas respuestas.

## 3. Reglas de limpieza

Una fila por decisión del EDA. **Una función, una prueba.** Se marca como vacío lo imposible; no se borran filas sin criterio.

Los nombres de función son una **propuesta** (en inglés, como pide `CLAUDE.md`); el grupo puede cambiarlos.

| # (de la tabla del EDA) | Columna(s) | Problema | Regla exacta (con el umbral o valor) | Función en `src/proyecto/data/cleaning.py` | Prueba en `tests/test_cleaning.py` |
|---|---|---|---|---|---|
| 1 | todas | 72.383 filas exactamente duplicadas (50 % del archivo) | Quitar filas idénticas en todas las columnas; conservar una | `drop_exact_duplicates` | `test_drop_exact_duplicates` |
| 2 | `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles`, `desemp_ingles`, `estu_estadoinvestigacion` | Fuga: son la respuesta o se conocen después del examen | Eliminar las 7 columnas (`punt_global` se conserva: es el objetivo) | `drop_leakage_columns` | `test_drop_leakage_columns` |
| 3 | `estu_consecutivo`, `estu_fechanacimiento` | Datos personales | `edad = 2022 − año de nacimiento` (edad aproximada); luego eliminar las dos columnas | `add_age_and_drop_personal` | `test_no_personal_columns` |
| 4 | `edad` | 30 estudiantes con edad menor de 13 años (incluso 0) | `edad < 13` → vacío; la fila se conserva. Los adultos (hasta más de 60) se dejan: son plausibles | `mark_impossible_age` | `test_mark_impossible_age` |
| 6 | `fami_educacionmadre`, `fami_educacionpadre`, `fami_estratovivienda` | Centinelas «No sabe», «No Aplica», «Sin Estrato» con puntajes distintos | No se convierten a vacío: «No sabe» y «No Aplica» se mantienen como categorías propias; «Sin Estrato» se conserva como la marca `sin_estrato` (regla 7b) | ninguna (la prueba comprueba que la limpieza no toca «No sabe» ni «No Aplica») | `test_sentinels_are_kept` |
| 7 | `fami_estratovivienda`, `fami_personashogar`, `fami_cuartoshogar` | Categorías ordenadas guardadas como texto | Estrato: `Estrato 1`…`Estrato 6` → 1…6. Personas: `1 a 2` → 1, `3 a 4` → 2, `5 a 6` → 3, `7 a 8` → 4, `9 o más` → 5. Cuartos: `Uno` → 1 … `Cinco` → 5, `Seis o mas` → 6. Vacío → vacío. «Sin Estrato»: ver la regla 7b | `encode_ordinal_columns` | `test_encode_ordinal_columns` |
| 7b (grupo, 31 oct 2026) | `fami_estratovivienda` → `fami_estratovivienda` (número) y `sin_estrato` (nueva) | «Sin Estrato» no cabe en la escala 1–6 y la decisión 6 pide conservarlo como marca propia | «Sin Estrato» → estrato **vacío (NaN), nunca 0**, y `sin_estrato` = 1. Vacío real → estrato vacío y `sin_estrato` = 0. `Estrato 1`…`Estrato 6` → 1…6 y `sin_estrato` = 0. El imputador del `Pipeline` (etapa 4) marca los vacíos con su indicador | `encode_ordinal_columns` | `test_sin_estrato_flag` |
| 6b (grupo, 31 oct 2026) | `fami_educacionmadre`, `fami_educacionpadre` | Escala de educación de los padres | La limpieza **no** cambia estas columnas: siguen como texto, con «No sabe» y «No Aplica» como categorías propias (decisión 6). Escala aprobada, que se aplica solo en la etapa 4 (`educacion_max_padres` en `add_features`): Ninguno 0, Primaria incompleta 1, Primaria completa 2, Secundaria incompleta 3, Secundaria completa 4, Técnica o tecnológica incompleta 5, Técnica o tecnológica completa 6, Educación profesional incompleta 7, Educación profesional completa 8, Postgrado 9. «No sabe» y «No Aplica» no entran en la escala | ninguna (se aplica en `src/proyecto/features/engineering.py`) | `test_sentinels_are_kept` (aquí) y `test_educacion_max_padres` (etapa 4) |
| 8 | `periodo`, `cole_cod_depto_ubicacion`, `cole_depto_ubicacion`, `estu_estudiante` | Un solo valor | Eliminar las 4 columnas | `drop_constant_columns` | `test_drop_constant_columns` |
| 9 | `cole_cod_dane_establecimiento`, `cole_codigo_icfes`, `cole_nombre_establecimiento`, `cole_nombre_sede` | Identificadores del colegio (1.071 a 1.807 valores distintos) | Eliminar las 4 columnas. `cole_cod_dane_sede` se conserva **solo para agrupar** y no entra como predictor (se excluye en la etapa 4) | `drop_school_identifiers` | `test_drop_school_identifiers` |
| 11 | `cole_calendario` | 235 estudiantes (0,3 %) en calendario «OTRO», en 3 sedes | Quitar las filas con `cole_calendario == "OTRO"`; el modelo aplica a calendario A | `keep_calendar_a` | `test_keep_calendar_a` |

> **Choque entre las decisiones 6 y 7, resuelto por el grupo el 31 oct 2026 (regla 7b):** la decisión 7 convierte el estrato
> en número, pero la 6 pide mantener «Sin Estrato» (1.561 estudiantes, puntaje promedio 211,2) como marca propia. Se
> aprobó la opción A: estrato numérico con «Sin Estrato» como vacío **más** la columna 0/1 `sin_estrato`.
>
> Las decisiones 5 y 10 no son limpieza: la 5 va en la sección 4 (vacíos, etapa 4) y la 10 es la partición (sección 1,
> `src/proyecto/data/split.py`).

## 4. Vacíos

| Columna | Qué significa el vacío | Tratamiento hoy | Tratamiento en la etapa 4 (dentro del `Pipeline`) |
|---|---|---|---|
| Columnas `fami_` (10,1 % de los estudiantes tiene algún vacío; 1.790 no respondieron ninguna) | ☐ no aplica ☒ no se anotó ☐ perdido ☐ imposible | ☒ dejar vacío ☐ categoría explícita ☐ reparar con valor de la entidad | Categoría propia «sin respuesta» (decisión 5): sacan ~18 puntos menos, el vacío es información |
| `fami_estratovivienda` numérico (vacío real o «Sin Estrato», regla 7b) | ☐ no aplica ☒ no se anotó ☐ perdido ☐ imposible | ☒ dejar vacío ☐ categoría explícita ☐ reparar con valor de la entidad | Mediana + indicador de vacío; `sin_estrato` distingue «Sin Estrato» del vacío real |
| `cole_bilingue` (16,4 % vacío) | ☐ no aplica ☒ no se anotó ☐ perdido ☐ imposible | ☒ dejar vacío ☐ categoría explícita ☐ reparar con valor de la entidad | Categoría propia «sin respuesta» (decisión 5): 16 puntos menos de promedio |
| `edad` (30 casos menores de 13, tras la decisión 4) | ☐ no aplica ☐ no se anotó ☐ perdido ☒ imposible | ☒ dejar vacío ☐ categoría explícita ☐ reparar con valor de la entidad | Mediana + indicador de vacío dentro del `Pipeline` (grupo, 31 oct 2026). En la etapa 3 solo se marcan como vacías las edades menores de 13 |

> Imputar con medias o medianas **no se hace aquí**: depende del entrenamiento y va dentro del `Pipeline`.

## 5. Entradas y salidas

| | Ruta |
|---|---|
| Entrada | `data/raw/saber11_antioquia_2022.csv` (nunca se modifica) |
| Salida: entrenamiento | `data/processed/train.joblib` |
| Salida: prueba (cerrada) | `data/processed/test.joblib` |
| Código de limpieza | `src/proyecto/data/cleaning.py` |
| Código de partición | `src/proyecto/data/split.py` |
| Notebook que orquesta | `notebooks/03_preprocesamiento.ipynb` (solo llama a las funciones) |

> **Cambios aprobados por el grupo el 31 oct 2026:**
> - **Formato `.joblib`** en vez de `.csv`/`.parquet`: conserva los tipos de datos (vacíos numéricos, enteros) y es lo
>   que escribe el notebook 03 y lee el notebook 04.
> - **`data/processed/` fuera de GitHub:** `.gitignore` ignora su contenido (`data/processed/*`) y conserva
>   `data/processed/.gitkeep`. Motivo: se regenera con el notebook 03, y la licencia CC BY-SA obliga a publicar con la
>   misma licencia cualquier versión modificada de los datos que se suba.
> - **`split_by_group`** como nombre de la función de partición (ver sección 1).

## 6. Pruebas que deben existir

- ☒ **Partición:** ninguna entidad aparece en dos particiones y no se pierde ninguna fila (`tests/test_split.py`).
- ☒ **La prueba de partición falla** si se cambia temporalmente a partición por fila (compruébenlo y vuelvan a dejarla bien).
  Comprobado a mano por Raúl Fernando Ossa Ramírez el 5 nov 2026: cambió `groups=df[group_col]` por `groups=df.index` en
  `split.py`, fallaron 3 pruebas de `tests/test_split.py` con «132 sedes aparecen en más de una
  partición» y lo revirtió con `git checkout`.
  (Lo comprueba el grupo a mano; además `test_row_split_would_share_schools` muestra que partir por fila comparte sedes.)
- ☒ **Una prueba por regla de limpieza** de la sección 3, con un caso normal y un caso sucio hechos a mano.
- ☒ **Datos personales:** el resultado de limpiar (`clean`) no contiene las columnas de la sección 2 (`load_raw_saber11`
  devuelve el archivo tal cual, como dice la sección 2).
- ☒ `pytest` en verde desde la raíz del repo (con `pytest.ini`, que limita la búsqueda a `tests/`, `pytest` a secas ya pasa: 62 de 62, y no choca con las
  pruebas de `material-del-curso/`.)

## 7. Criterios de cierre (H1)

- ☒ La limpieza corre **de principio a fin desde cero** (`data/processed/` borrada y regenerada con el notebook 03), sin pasos manuales.
- ☒ Unidad de análisis y forma de partir **escritas** (sección 1) y documentadas en `reports/01_eda.md`.
- ☒ `pytest` en verde (`pytest tests`: 52 de 52).
- ☒ Conjunto de prueba guardado y sin mirar (solo se contaron filas y sedes).
- ☒ `data/raw/` intacta (misma huella SHA-256 antes y después) y `.env` fuera de Git (`git status`).
- ☒ Todo subido a GitHub.
- ☐ Revisaron el código de Claude con `checklist-revision-ia.md` y cada integrante puede explicar una función.
- ☒ **Hallazgo que no esperaban** (para la puesta en común): la mitad del archivo original (72.383 filas) eran
  duplicados exactos.
