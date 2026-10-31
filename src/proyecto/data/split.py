"""Partición por sede del colegio (decisión 10 del EDA).

La sede sola explica el 36 % de la variación del puntaje y la app recibirá colegios que el modelo no vio. Si se parte
por fila, estudiantes de una misma sede caen a los dos lados y el MAE sale optimista. Aquí **todas** las particiones
mantienen cada sede completa en un solo lado.
"""
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit

GROUP_COL = "cole_cod_dane_sede"
RANDOM_STATE = 42


def split_by_group(
    df: pd.DataFrame, group_col: str = GROUP_COL, test_size: float = 0.2, seed: int = RANDOM_STATE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa entrenamiento y prueba sin repartir ninguna sede entre los dos (`test_size` es la fracción de sedes)."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(splitter.split(df, groups=df[group_col]))
    train = df.iloc[train_idx].reset_index(drop=True)
    test = df.iloc[test_idx].reset_index(drop=True)
    assert_disjoint_groups(train, test, group_col=group_col)
    return train, test


def assert_disjoint_groups(*frames: pd.DataFrame, group_col: str = GROUP_COL) -> None:
    """Falla si alguna sede aparece en más de una partición."""
    seen: set = set()
    for i, frame in enumerate(frames):
        groups = set(frame[group_col])
        overlap = seen & groups
        if overlap:
            raise AssertionError(f"{len(overlap)} sedes aparecen en más de una partición (partición {i})")
        seen |= groups


def group_cv(n_splits: int = 5) -> GroupKFold:
    """Validación cruzada que mantiene cada sede completa en un solo pliegue (regresión: sin estratificar)."""
    return GroupKFold(n_splits=n_splits)
