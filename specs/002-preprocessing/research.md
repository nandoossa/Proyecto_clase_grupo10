# Research: Limpieza y partición de los datos (etapa 3)

No quedaron `NEEDS CLARIFICATION`: `especificaciones/03-preprocesamiento.md` está cerrada. Estas son las decisiones de
diseño y lo que se verificó en `data/raw/` el 31 oct 2026.

## 1. Orden de la limpieza

- **Decision**: `clean(df)` aplica, en este orden: duplicados (1) → columnas con fuga (2) → edad y datos personales (3) →
  edad imposible (4) → ordinales y `sin_estrato` (7, 7b) → columnas constantes (8) → identificadores del colegio (9) →
  calendario A (11).
- **Rationale**: los duplicados van primero porque `estu_consecutivo` es parte de la fila idéntica (quitarlo antes podría
  juntar a dos estudiantes distintos). La edad necesita la fecha antes de borrarla. El calendario va al final porque
  `cole_calendario` no se elimina antes.
- **Alternatives considered**: filtrar calendario primero (mismo resultado, pero mezcla el filtro de filas con las reglas
  de columnas).

## 2. Edad

- **Decision**: `pd.to_datetime(fecha, format="%d/%m/%Y", errors="coerce")`; `edad = 2022 − año`. Ilegible → vacío.
- **Verificado en los datos**: 0 fechas vacías, 0 ilegibles; 30 edades < 13 (mínimo 0), 28 > 60 (máximo 80).
- **Rationale**: formato único `dd/mm/aaaa`; `errors="coerce"` evita que una fecha mala detenga todo.

## 3. Ordinales

- **Decision**: diccionarios explícitos con el texto exacto de los datos: estrato `Estrato 1`…`Estrato 6`; personas
  `1 a 2`, `3 a 4`, `5 a 6`, `7 a 8`, `9 o más` (con tilde); cuartos `Uno`, `Dos`, `Tres`, `Cuatro`, `Cinco`,
  `Seis o mas` (sin tilde). Cualquier texto no previsto → vacío **y** la prueba lo detecta.
- **Verificado en los datos**: son exactamente esos valores (las tildes del archivo están bien; lo que se veía dañado era
  la consola de Windows).
- **Rationale**: un diccionario se puede leer y discutir; una conversión «inteligente» escondería errores.

## 4. Partición

- **Decision**: `split_by_group(df, group_col="cole_cod_dane_sede", test_size=0.2, seed=42)` con `GroupShuffleSplit`, y
  `assert_disjoint_groups(*frames, group_col)` que falla si una sede aparece en dos particiones. `group_cv(n_splits=5)`
  devuelve `GroupKFold` para las etapas siguientes.
- **Rationale**: misma forma que el ejemplo (`split_by_customer`, `assert_disjoint_customers`, `group_cv`) y la firma que
  ya espera la plantilla del notebook 03 (`split_by_group(df, group_col, test_size, seed)`). `GroupKFold` y no
  `StratifiedGroupKFold` porque es regresión.
- **Nota**: el 20 % es de sedes; el porcentaje de filas en prueba será cercano a 20 %, no exacto.

## 5. Formato de salida

- **Decision**: `data/processed/train.joblib` y `test.joblib`.
- **Rationale**: es lo que escribe la plantilla del notebook 03 y lo que lee el notebook 04. La especificación decía
  `train.csv (o .parquet)`; joblib conserva los tipos (vacíos numéricos, enteros) sin conversión. Se anota la diferencia.

## 6. `.gitignore`

- **Decision**: agregar `data/processed/*` (con `!data/processed/.gitkeep`).
- **Rationale**: hoy no está ignorada; el notebook dice que no se versiona; la licencia CC BY-SA obliga a publicar con la
  misma licencia cualquier versión modificada que se suba, y el grupo no decidió publicarla.

## 7. Compatibilidad con la etapa 4

- **Decision**: una prueba (`test_clean_output_matches_feature_stage`) limpia una tabla hecha a mano con el formato crudo y
  comprueba que contiene todas las columnas de `feature_columns(use_engineered=True)` con los códigos esperados, y que
  `build_preprocessor` y `add_features` funcionan sobre ella.
- **Verificación del contrato** (sección «Compatibilidad» de `data-model.md`): coinciden `edad`, `fami_estratovivienda`
  (1–6 o vacío), `sin_estrato` (0/1), `fami_personashogar` (1–5), `fami_cuartoshogar` (1–6), las 14 categóricas y los
  2 códigos de municipio.
