"""Utilidades de MLflow: setup de experimentos y registro de modelos."""

import json
import os
import tempfile

import mlflow


def setup_experiment(experiment_name: str) -> str:
    """Crea el experimento si no existe y lo activa. Retorna el experiment_id."""
    mlflow.set_tracking_uri(os.environ.get(
        "MLFLOW_TRACKING_URI", "http://mlflow-proxy:5001"
    ))
    exp = mlflow.get_experiment_by_name(experiment_name)
    if exp is None:
        exp_id = mlflow.create_experiment(experiment_name)
    else:
        exp_id = exp.experiment_id
    mlflow.set_experiment(experiment_name)
    return exp_id


def log_feature_columns(columns: list[str]) -> None:
    """Loguea la lista de columnas como artefacto JSON en el run activo."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "feature_columns.json")
        with open(path, "w") as f:
            json.dump(columns, f)
        mlflow.log_artifact(path)


def register_model(run_id: str, model_name: str) -> str:
    """Registra el modelo de un run en el Model Registry. Retorna la version."""
    model_uri = f"runs:/{run_id}/model"
    result = mlflow.register_model(model_uri, model_name)
    return result.version
