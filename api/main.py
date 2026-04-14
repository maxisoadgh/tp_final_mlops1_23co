"""API de inferencia — satisfaccion de pasajeros de aerolineas."""

import json
import logging
import sys
from contextlib import asynccontextmanager

import mlflow
import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException

sys.path.insert(0, "/app")

from src.config import REGISTERED_MODEL_NAME
from src.preprocessing import prepare_single_prediction
from schemas import (
    FIELD_TO_COLUMN,
    APIInfo,
    HealthResponse,
    PassengerFeatures,
    PredictionResponse,
)

logger = logging.getLogger("uvicorn.error")

model = None
model_version = "unknown"
feature_columns: list[str] | None = None


def _load_model() -> None:
    """Carga el modelo y la lista de columnas desde MLflow Registry."""
    global model, model_version, feature_columns

    client = mlflow.MlflowClient()
    versions = client.search_model_versions(f"name='{REGISTERED_MODEL_NAME}'")
    if not versions:
        raise RuntimeError(f"No hay versiones de '{REGISTERED_MODEL_NAME}' en el registry")

    latest = sorted(versions, key=lambda v: int(v.version))[-1]
    run_id = latest.run_id
    model_version = latest.version

    logger.info(f"Cargando modelo {REGISTERED_MODEL_NAME} v{model_version} (run={run_id[:8]}) ...")

    model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

    local_path = client.download_artifacts(run_id, "feature_columns.json")
    with open(local_path) as f:
        feature_columns = json.load(f)

    logger.info(f"Modelo cargado: {type(model).__name__}, {len(feature_columns)} features")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _load_model()
    except Exception as e:
        logger.warning(f"No se pudo cargar el modelo al inicio: {e}")
    yield


app = FastAPI(
    title="Airline Satisfaction Prediction API",
    description="Prediccion de satisfaccion de pasajeros. Modelo entrenado con MLflow.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_model=APIInfo)
async def get_api_info() -> APIInfo:
    return APIInfo()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=model is not None,
    )


@app.post("/reload", response_model=HealthResponse)
async def reload_model() -> HealthResponse:
    """Recarga el modelo desde MLflow Registry."""
    try:
        _load_model()
        return HealthResponse(status="model reloaded", model_loaded=True)
    except Exception as e:
        logger.error(f"Error recargando modelo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: PassengerFeatures) -> PredictionResponse:
    """Predice la satisfaccion de un pasajero."""
    if model is None or feature_columns is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible. Ejecutar el DAG de entrenamiento antes.",
        )

    raw_features = {
        FIELD_TO_COLUMN[k]: v
        for k, v in features.model_dump().items()
    }
    df = prepare_single_prediction(raw_features, feature_columns)

    pred_label = model.predict(df)[0]
    prediction_str = "satisfied" if pred_label == 1 else "neutral or dissatisfied"

    prob_satisfied = 0.5
    if hasattr(model, "predict_proba"):
        probas = model.predict_proba(df)[0]
        prob_satisfied = float(probas[1])

    return PredictionResponse(
        prediction=prediction_str,
        probability_satisfied=round(prob_satisfied, 4),
        model_version=model_version,
    )
