"""Evaluacion, comparacion de modelos y registro del mejor."""

import math

import mlflow
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from src.mlflow_utils import register_model


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calcula precision, recall, f1 y accuracy."""
    return {
        "precision": round(precision_score(y_true, y_pred), 4),
        "recall": round(recall_score(y_true, y_pred), 4),
        "f1": round(f1_score(y_true, y_pred), 4),
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
    }


def select_best_run(results: list[dict]) -> dict:
    """Selecciona el resultado con mayor f1_score."""
    return max(results, key=lambda r: r["f1_score"])


def register_best_model(results: list[dict], model_name: str) -> dict:
    """Selecciona el mejor modelo y lo registra en MLflow Model Registry."""
    best = select_best_run(results)
    version = register_model(best["run_id"], model_name)
    return {
        "model_name": best["model_name"],
        "f1_score": best["f1_score"],
        "run_id": best["run_id"],
        "registry_version": version,
    }
