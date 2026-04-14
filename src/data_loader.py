"""Carga y preparacion del dataset de aerolineas."""

import pandas as pd

from src.config import (
    CATEGORICAL_COLS,
    DROP_COLS,
    SATISFIED_LABEL,
    TARGET_COL,
)


def load_dataset(path: str) -> pd.DataFrame:
    """
    Lee un CSV y aplica limpieza basica.

    Elimina la columna ``id`` y las filas con nulos en
    ``Arrival Delay in Minutes`` (~0.3% del dataset).
    """
    df = pd.read_csv(path, index_col=0)
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")
    df = df.dropna(subset=["Arrival Delay in Minutes"])
    return df


def encode_target(y: pd.Series) -> pd.Series:
    """Convierte la columna de satisfaccion a binario (1=satisfied, 0=otro)."""
    return (y == SATISFIED_LABEL).astype(int)


def prepare_features_target(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Separa features y target, aplica one-hot encoding a las categoricas.

    Replica ``pd.get_dummies(X, columns=CATEGORICAL_COLS, drop_first=True)``.
    """
    y = encode_target(df[TARGET_COL])
    X = df.drop(columns=[TARGET_COL])
    X = pd.get_dummies(X, columns=CATEGORICAL_COLS, drop_first=True)
    return X, y
