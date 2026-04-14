"""Pipeline de preprocesamiento (ColumnTransformer + sklearn Pipeline)."""

import json

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from src.config import CATEGORICAL_COLS, NUMERIC_COLS


def build_preprocessor(
    numeric_cols: list[str],
    rating_cols: list[str],
) -> ColumnTransformer:
    """StandardScaler para numericas, MinMaxScaler para ratings + dummies."""
    return ColumnTransformer([
        ("scaler", StandardScaler(), numeric_cols),
        ("minmax", MinMaxScaler(), rating_cols),
    ])


def build_pipeline(
    model,
    preprocessor: ColumnTransformer | None = None,
) -> Pipeline:
    """Envuelve preprocessor + modelo en un Pipeline de sklearn."""
    if preprocessor is not None:
        return Pipeline([("pre", preprocessor), ("cls", model)])
    return Pipeline([("cls", model)])


def get_rating_cols(X: pd.DataFrame) -> list[str]:
    """Columnas que no son numericas (ratings + dummies post-get_dummies)."""
    return [c for c in X.columns if c not in NUMERIC_COLS]


def prepare_single_prediction(
    features: dict,
    expected_columns: list[str],
) -> pd.DataFrame:
    """
    Convierte un dict de features a un DataFrame alineado con las columnas
    que el modelo espera. Aplica get_dummies y rellena columnas faltantes con 0.
    """
    df = pd.DataFrame([features])
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)

    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[expected_columns]

    return df


def save_feature_columns(columns: list[str], path: str) -> None:
    with open(path, "w") as f:
        json.dump(columns, f)


def load_feature_columns(path: str) -> list[str]:
    with open(path) as f:
        return json.load(f)
