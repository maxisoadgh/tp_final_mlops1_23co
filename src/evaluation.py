"""Evaluacion, métricas, gráficas, comparación de modelos y registro del mejor."""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from src.mlflow_utils import register_model


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calcula precision, recall, f1 y accuracy."""
    return {
        "test_precision": round(precision_score(y_true, y_pred), 4),
        "test_recall": round(recall_score(y_true, y_pred), 4),
        "test_f1": round(f1_score(y_true, y_pred), 4),
        "test_accuracy": round(accuracy_score(y_true, y_pred), 4),
    }


def build_confusion_matrix_figure(
    y_true: np.ndarray, y_pred: np.ndarray
):
    """Construye la figura de matriz de confusion para un clasificador binario."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        display_labels=["neutral or dissatisfied", "satisfied"],
        cmap="Blues",
        colorbar=False,
        ax=ax,
    )
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    return fig


def build_feature_importance_figure(
    feature_names: list[str],
    importances: np.ndarray,
    top_n: int = 15,
    title: str | None = None,
):
    """Construye un barplot horizontal de importancias ordenadas."""
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "value": importances,
    }).sort_values("value", ascending=False).head(top_n)
    importance_df = importance_df.sort_values("value", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(importance_df["feature"], importance_df["value"], color="#2E86AB")
    ax.set_title(title or "Feature Importance")
    ax.set_xlabel("Importance")
    ax.set_ylabel("Feature")
    fig.tight_layout()
    return fig


def build_logistic_coefficients_figure(
    feature_names: list[str],
    coefficients: np.ndarray,
    top_n: int = 15,
    title: str | None = None,
):
    """Construye un barplot de coeficientes ordenados por magnitud."""
    coef_df = pd.DataFrame({
        "feature": feature_names,
        "coefficient": coefficients,
    })
    coef_df["abs_coefficient"] = coef_df["coefficient"].abs()
    coef_df = coef_df.sort_values(
        "abs_coefficient", ascending=False
    ).head(top_n)
    coef_df = coef_df.sort_values("coefficient", ascending=True)

    colors = ["#C44E52" if c < 0 else "#55A868" for c in coef_df["coefficient"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(coef_df["feature"], coef_df["coefficient"], color=colors)
    ax.set_title(title or "Logistic Regression Coefficients")
    ax.set_xlabel("Coefficient")
    ax.set_ylabel("Feature")
    ax.axvline(0, color="black", linewidth=1)
    fig.tight_layout()
    return fig


def build_roc_curve_figure(y_true: np.ndarray, y_score: np.ndarray):
    """Construye la curva ROC a partir de scores o probabilidades."""
    fig, ax = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(y_true, y_score, ax=ax)
    ax.set_title("ROC Curve")
    fig.tight_layout()
    return fig


def build_precision_recall_curve_figure(
    y_true: np.ndarray, y_score: np.ndarray
):
    """Construye la curva Precision-Recall a partir de scores o probabilidades."""
    fig, ax = plt.subplots(figsize=(6, 5))
    PrecisionRecallDisplay.from_predictions(y_true, y_score, ax=ax)
    ax.set_title("Precision-Recall Curve")
    fig.tight_layout()
    return fig


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
