# Contrato: `src/proyecto/features/engineering.py`

Misma estructura que el ejemplo de CreditSight; las columnas son de Saber 11.

## Constantes públicas

- `NUMERIC_BASE`, `CATEGORICAL_BASE`, `MUNICIPALITY_CODES`: columnas base (ver `data-model.md`).
- `NUMERIC_ENGINEERED`: `["n_bienes_hogar", "educacion_max_padres", "personas_por_cuarto", "vive_en_mcpio_colegio"]`.
- `FORBIDDEN_COLUMNS`: las 16 columnas prohibidas como predictor (ver `data-model.md`), incluida `estu_tipodocumento`.
- `PARENT_EDUCATION_LEVELS`: escala de educación (texto → 0–9).

## `add_features(df: pd.DataFrame) -> pd.DataFrame`

- Devuelve una **copia** con las 4 variables nuevas; no modifica `df`.
- Divisiones por cero o con datos faltantes → `NaN`, nunca `inf`.

## `feature_columns(use_engineered: bool = False, extra_numeric: list[str] | None = None) -> tuple[list[str], list[str]]`

- Devuelve `(numéricas, categóricas)`. Las categóricas incluyen los códigos de municipio.
- Con `use_engineered=False` no incluye ninguna variable nueva.
- Ninguna columna de `FORBIDDEN_COLUMNS` aparece nunca. Si `extra_numeric` trae una columna prohibida → `ValueError`.

## `build_preprocessor(scale: bool = True, use_engineered: bool = False, extra_numeric: list[str] | None = None, min_frequency: float = 0.01) -> ColumnTransformer`

- Numéricas: `SimpleImputer(median, add_indicator=True)` + `StandardScaler` (si `scale`).
- Categóricas (incluye municipios convertidos a texto): `SimpleImputer(constant, "sin respuesta")` +
  `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=min_frequency)`.
- `remainder="drop"`: cualquier otra columna de la entrada se ignora.
