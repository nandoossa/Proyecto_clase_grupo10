"""Limpieza de los datos de Saber 11 (etapa 3).

Una función por regla de `especificaciones/03-preprocesamiento.md` (sección 3), aplicadas en orden por `clean`.
Cada función devuelve una tabla nueva: el original no cambia. Aquí no se imputa nada: imputar depende del
entrenamiento y va dentro del `Pipeline` (etapa 4).
"""
import pandas as pd

TEST_YEAR = 2022  # periodo 20224
MIN_AGE = 13

LEAKAGE_COLUMNS = [
    "punt_matematicas",
    "punt_lectura_critica",
    "punt_sociales_ciudadanas",
    "punt_c_naturales",
    "punt_ingles",
    "desemp_ingles",
    "estu_estadoinvestigacion",
]
PERSONAL_COLUMNS = ["estu_consecutivo", "estu_fechanacimiento"]
CONSTANT_COLUMNS = ["periodo", "cole_cod_depto_ubicacion", "cole_depto_ubicacion", "estu_estudiante"]
# cole_cod_dane_sede no está aquí: se conserva para agrupar al partir.
SCHOOL_ID_COLUMNS = [
    "cole_cod_dane_establecimiento",
    "cole_codigo_icfes",
    "cole_nombre_establecimiento",
    "cole_nombre_sede",
]

NO_STRATUM = "Sin Estrato"
STRATUM_CODES = {f"Estrato {level}": level for level in range(1, 7)}
HOUSEHOLD_SIZE_CODES = {"1 a 2": 1, "3 a 4": 2, "5 a 6": 3, "7 a 8": 4, "9 o más": 5}
ROOM_CODES = {"Uno": 1, "Dos": 2, "Tres": 3, "Cuatro": 4, "Cinco": 5, "Seis o mas": 6}


def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 1: cada estudiante viene dos veces en la fuente; se deja una fila."""
    return df.drop_duplicates().reset_index(drop=True)


def drop_leakage_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 2: puntajes por área y columnas que se conocen después del examen."""
    return df.drop(columns=LEAKAGE_COLUMNS)


def add_age_and_drop_personal(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 3: edad aproximada (año de la prueba - año de nacimiento) y fuera los datos personales."""
    out = df.copy()
    birth = pd.to_datetime(out["estu_fechanacimiento"], format="%d/%m/%Y", errors="coerce")
    out["edad"] = (TEST_YEAR - birth.dt.year).astype(float)
    return out.drop(columns=PERSONAL_COLUMNS)


def mark_impossible_age(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 4: menos de 13 años es imposible en Saber 11 -> vacío; la fila se conserva."""
    out = df.copy()
    out["edad"] = out["edad"].where(out["edad"] >= MIN_AGE)
    return out


def encode_ordinal_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Reglas 7 y 7b: estrato, personas y cuartos como números ordenados.

    «Sin Estrato» queda vacío en el estrato (nunca 0) y se marca con sin_estrato = 1. Un texto no previsto queda vacío.
    """
    out = df.copy()
    out["sin_estrato"] = (out["fami_estratovivienda"] == NO_STRATUM).astype(int)
    out["fami_estratovivienda"] = out["fami_estratovivienda"].map(STRATUM_CODES).astype(float)
    out["fami_personashogar"] = out["fami_personashogar"].map(HOUSEHOLD_SIZE_CODES).astype(float)
    out["fami_cuartoshogar"] = out["fami_cuartoshogar"].map(ROOM_CODES).astype(float)
    return out


def drop_constant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 8: columnas con un solo valor en todo el archivo."""
    return df.drop(columns=CONSTANT_COLUMNS)


def drop_school_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 9: identificadores del colegio (el modelo memorizaría cada colegio en vez de aprender de sus atributos)."""
    return df.drop(columns=SCHOOL_ID_COLUMNS)


def keep_calendar_a(df: pd.DataFrame) -> pd.DataFrame:
    """Regla 11: el modelo aplica a calendario A; «OTRO» tiene muy pocos casos."""
    return df[df["cole_calendario"] == "A"].reset_index(drop=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas las reglas. Los duplicados van primero: estu_consecutivo es parte de la fila idéntica.

    Las reglas 6 y 6b no tienen función: «No sabe» y «No Aplica» en la educación de los padres no se tocan.
    """
    out = drop_exact_duplicates(df)
    out = drop_leakage_columns(out)
    out = add_age_and_drop_personal(out)
    out = mark_impossible_age(out)
    out = encode_ordinal_columns(out)
    out = drop_constant_columns(out)
    out = drop_school_identifiers(out)
    return keep_calendar_a(out)
