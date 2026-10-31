"""Pruebas de la partición por sede (etapa 3, decisión 10 del EDA)."""
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from proyecto.data.split import GROUP_COL, assert_disjoint_groups, group_cv, split_by_group


def _schools(n_schools: int = 200, students: int = 5) -> pd.DataFrame:
    """Tabla hecha a mano: `n_schools` sedes con `students` estudiantes cada una."""
    rng = np.random.default_rng(0)
    rows = [
        {GROUP_COL: 1000 + s, "x": rng.random(), "punt_global": int(rng.integers(100, 478))}
        for s in range(n_schools)
        for _ in range(students)
    ]
    return pd.DataFrame(rows)


def test_split_never_shares_a_school_between_train_and_test():
    df = _schools()
    train, test = split_by_group(df, test_size=0.2, seed=42)
    assert set(train[GROUP_COL]).isdisjoint(test[GROUP_COL])
    assert len(train) + len(test) == len(df)


def test_split_keeps_each_school_together():
    train, test = split_by_group(_schools(), test_size=0.2, seed=42)
    assert (train.groupby(GROUP_COL).size() == 5).all()
    assert (test.groupby(GROUP_COL).size() == 5).all()


def test_assert_disjoint_raises_on_overlap():
    df = _schools(10)
    with pytest.raises(AssertionError):
        assert_disjoint_groups(df.iloc[:20], df.iloc[18:30])


def test_row_split_would_share_schools():
    # Por qué se parte por sede: una partición por fila reparte estudiantes de una misma sede a los dos lados.
    df = _schools()
    train, test = train_test_split(df, test_size=0.2, random_state=42)
    assert not set(train[GROUP_COL]).isdisjoint(test[GROUP_COL])
    with pytest.raises(AssertionError):
        assert_disjoint_groups(train, test)


def test_group_cv_folds_do_not_share_schools():
    df = _schools()
    for train_idx, valid_idx in group_cv(5).split(df, df["punt_global"], groups=df[GROUP_COL]):
        assert set(df[GROUP_COL].iloc[train_idx]).isdisjoint(df[GROUP_COL].iloc[valid_idx])


def test_split_is_reproducible():
    df = _schools()
    train_a, test_a = split_by_group(df, seed=42)
    train_b, test_b = split_by_group(df, seed=42)
    pd.testing.assert_frame_equal(test_a, test_b)
    assert 0.10 <= len(test_a) / len(df) <= 0.30
