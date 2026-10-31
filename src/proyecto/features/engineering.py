"""Variables nuevas y preprocesamiento del modelo (etapa 4).

Recibe la tabla que entrega la limpieza de la etapa 3. `add_features` solo usa columnas de la misma fila que se
conocen antes del examen. Las variables nuevas quedan apagadas por defecto (`use_engineered=False`): el notebook 04
mide con validación agrupada por sede si bajan el MAE, y solo entonces se encienden.
Reglas y motivos: `especificaciones/04-features.md`.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

# Ordinales que crea la etapa 3; «Sin Estrato» llega como estrato vacío y sin_estrato = 1 (regla 7b).
NUMERIC_BASE = [
    "edad",
    "fami_estratovivienda",
    "sin_estrato",
    "fami_personashogar",
    "fami_cuartoshogar",
]
CATEGORICAL_BASE = [
    "cole_area_ubicacion",
    "cole_bilingue",
    "cole_caracter",
    "cole_genero",
    "cole_jornada",
    "cole_naturaleza",
    "cole_sede_principal",
    "estu_genero",
    "fami_educacionmadre",
    "fami_educacionpadre",
    "fami_tieneautomovil",
    "fami_tienecomputador",
    "fami_tieneinternet",
    "fami_tienelavadora",
]
# Códigos y no nombres: «ARMENIA» corresponde a dos municipios de residencia distintos.
MUNICIPALITY_CODES = ["cole_cod_mcpio_ubicacion", "estu_cod_reside_mcpio"]
NUMERIC_ENGINEERED = [
    "n_bienes_hogar",
    "educacion_max_padres",
    "personas_por_cuarto",
    "vive_en_mcpio_colegio",
]
# Nunca entran como predictor: objetivo, fuga, datos personales, identificadores y exclusiones por equidad.
FORBIDDEN_COLUMNS = [
    "punt_global",
    "punt_matematicas",
    "punt_lectura_critica",
    "punt_sociales_ciudadanas",
    "punt_c_naturales",
    "punt_ingles",
    "desemp_ingles",
    "estu_estadoinvestigacion",
    "estu_consecutivo",
    "estu_fechanacimiento",
    "cole_cod_dane_sede",
    "cole_cod_dane_establecimiento",
    "cole_codigo_icfes",
    "cole_nombre_establecimiento",
    "cole_nombre_sede",
    "estu_tipodocumento",
    "estu_nacionalidad",
    "estu_privado_libertad",
]

HOUSEHOLD_ASSETS = ["fami_tieneautomovil", "fami_tienecomputador", "fami_tieneinternet", "fami_tienelavadora"]
# Escala confirmada por el grupo (31 oct 2026). «No sabe» y «No Aplica» quedan fuera: cuentan como vacío.
PARENT_EDUCATION_LEVELS = {
    "Ninguno": 0,
    "Primaria incompleta": 1,
    "Primaria completa": 2,
    "Secundaria (Bachillerato) incompleta": 3,
    "Secundaria (Bachillerato) completa": 4,
    "Técnica o tecnológica incompleta": 5,
    "Técnica o tecnológica completa": 6,
    "Educación profesional incompleta": 7,
    "Educación profesional completa": 8,
    "Postgrado": 9,
}
# Código de personas de la etapa 3 (1 = «1 a 2» … 5 = «9 o más») -> punto medio del rango.
HOUSEHOLD_SIZE_MIDPOINTS = {1: 1.5, 2: 3.5, 3: 5.5, 4: 7.5, 5: 9.0}


def _ratio(num: pd.Series, den: pd.Series) -> pd.Series:
    """División segura: denominador cero o ausente -> NaN."""
    return num / den.where(den > 0)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Añade bienes del hogar, educación más alta de los padres, hacinamiento y municipio. No modifica el original."""
    out = df.copy()

    assets = out[HOUSEHOLD_ASSETS]
    out["n_bienes_hogar"] = (assets == "Si").sum(axis=1).astype(float).where(assets.notna().any(axis=1))

    education = out[["fami_educacionmadre", "fami_educacionpadre"]].apply(lambda col: col.map(PARENT_EDUCATION_LEVELS))
    out["educacion_max_padres"] = education.max(axis=1)

    people = out["fami_personashogar"].map(HOUSEHOLD_SIZE_MIDPOINTS)
    out["personas_por_cuarto"] = _ratio(people, out["fami_cuartoshogar"])

    school, home = out["cole_cod_mcpio_ubicacion"], out["estu_cod_reside_mcpio"]
    out["vive_en_mcpio_colegio"] = (school == home).astype(float).where(school.notna() & home.notna())
    return out


def feature_columns(
    use_engineered: bool = False, extra_numeric: list[str] | None = None
) -> tuple[list[str], list[str]]:
    """Devuelve (numéricas, categóricas) que usa el modelo; las categóricas incluyen los códigos de municipio.

    `extra_numeric` permite probar columnas adicionales sin tocar el código, pero nunca una prohibida.
    """
    extra = list(extra_numeric or [])
    forbidden = sorted(set(extra) & set(FORBIDDEN_COLUMNS))
    if forbidden:
        raise ValueError(f"Columnas prohibidas como predictor: {forbidden}")
    numeric = NUMERIC_BASE + (NUMERIC_ENGINEERED if use_engineered else []) + extra
    return numeric, CATEGORICAL_BASE + MUNICIPALITY_CODES


def _as_text(X: pd.DataFrame) -> pd.DataFrame:
    """Convierte a texto sin tocar los vacíos; 5001 y 5001.0 quedan iguales ("5001")."""

    def to_text(value):
        if pd.isna(value):
            return np.nan
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    return pd.DataFrame(X).apply(lambda col: col.map(to_text)).astype(object)


def build_preprocessor(
    scale: bool = True,
    use_engineered: bool = False,
    extra_numeric: list[str] | None = None,
    min_frequency: float | None = 0.01,
) -> ColumnTransformer:
    """Imputación + escalado de numéricas y one-hot de categóricas, ajustados solo con entrenamiento.

    Vacíos categóricos -> «sin respuesta» (decisión 5); «No sabe» y «No Aplica» quedan como categorías propias
    (decisión 6). Las categorías con menos de `min_frequency` de los estudiantes, y las nunca vistas, van a un
    grupo «poco frecuente»; `min_frequency=None` no agrupa.
    """
    numeric, categorical = feature_columns(use_engineered, extra_numeric)
    numeric_steps = [("impute", SimpleImputer(strategy="median", add_indicator=True))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))
    categorical_steps = [
        ("text", FunctionTransformer(_as_text, feature_names_out="one-to-one")),
        ("impute", SimpleImputer(strategy="constant", fill_value="sin respuesta")),
        ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=min_frequency, sparse_output=False)),
    ]
    return ColumnTransformer(
        [
            ("num", Pipeline(numeric_steps), numeric),
            ("cat", Pipeline(categorical_steps), categorical),
        ],
        remainder="drop",
    )
