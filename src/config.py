"""Configuracion del proyecto."""

import os


RANDOM_STATE = 42

TARGET_COL = "satisfaction"
SATISFIED_LABEL = "satisfied"

CATEGORICAL_COLS = [
    "Gender",
    "Customer Type",
    "Type of Travel",
    "Class",
]

NUMERIC_COLS = [
    "Age",
    "Flight Distance",
    "Departure Delay in Minutes",
    "Arrival Delay in Minutes",
]

RATING_COLS = [
    "Inflight wifi service",
    "Departure/Arrival time convenient",
    "Ease of Online booking",
    "Gate location",
    "Food and drink",
    "Online boarding",
    "Seat comfort",
    "Inflight entertainment",
    "On-board service",
    "Leg room service",
    "Baggage handling",
    "Checkin service",
    "Inflight service",
    "Cleanliness",
]

DROP_COLS = ["id"]


EXPERIMENT_NAME = "airline-satisfaction"
REGISTERED_MODEL_NAME = "airline-satisfaction-best"


def get_mlflow_tracking_uri() -> str:
    """Obtiene la URI de tracking de MLflow desde env vars."""
    return os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow-proxy:5001")


def get_data_path(base_dir: str, filename: str) -> str:
    """Construye la ruta completa a un archivo de datos."""
    return os.path.join(base_dir, "aerolineas", filename)
