# Stack tecnológico

## Servicios y versiones

| Servicio | Imagen | Puerto(s) | Rol |
|----------|--------|-----------|-----|
| **PostgreSQL** | `postgres:14.19-trixie` | `5432` | Backend store de MLflow y metadata de Airflow |
| **Redis / Valkey** | `valkey/valkey:8.1-bookworm` | `6379` (interno) | Broker Celery para Airflow |
| **MinIO** | `minio/minio:latest` | `9000` (API), `9001` (UI) | Artifact store S3-compatible |
| **MLflow** | `./dockerfiles/mlflow` (Python 3.12-slim) | `5000` | Tracking server + Model Registry |
| **mlflow-proxy** | `nginx:alpine` | `5001` (interno) | Proxy nginx — workaround DNS rebinding |
| **JupyterLab** | `./dockerfiles/jupyter` (Python 3.12-slim) | `8888` | Experimentación |
| **FastAPI** | `./dockerfiles/api` (Python 3.12-slim) | `8000` | Serving de predicciones |
| **Streamlit** | `./dockerfiles/streamlit` (Python 3.12-slim) | `8501` | Frontend web de predicción |
| **Airflow** | `apache/airflow:3.0.2` | `8080` | Orquestación (CeleryExecutor) |

## Paquetes Python principales

=== "Airflow worker"
    ```
    pandas · scikit-learn · mlflow · boto3
    xgboost · optuna · optuna-integration[xgboost]
    ```

=== "JupyterLab"
    ```
    jupyterlab · pandas · numpy · scikit-learn
    matplotlib · seaborn · mlflow[extras] · boto3
    xgboost · optuna · optuna-integration[xgboost]
    dython · ipywidgets
    ```

=== "FastAPI"
    ```
    fastapi · uvicorn[standard] · mlflow[extras]
    boto3 · pandas · scikit-learn · pydantic · xgboost
    ```

=== "MLflow server"
    ```
    mlflow[extras] · psycopg2-binary · boto3
    cryptography · pymysql · pandas · numpy · scikit-learn
    ```

## Módulos Python compartidos (`src/`)

El directorio `src/` se monta en los tres entornos que necesitan el código de ML:

| Módulo | Responsabilidad |
|--------|----------------|
| `config.py` | Constantes, columnas del dataset, paths, nombres de experimento |
| `data_loader.py` | Carga CSV, limpieza, one-hot encoding, separación features/target |
| `preprocessing.py` | `ColumnTransformer` (StandardScaler + MinMaxScaler), `prepare_single_prediction` |
| `training.py` | Entrenamiento de 4 modelos con Optuna + logging MLflow |
| `evaluation.py` | Métricas, selección del mejor modelo, registro en Registry |
| `mlflow_utils.py` | Setup de experimentos, `log_feature_columns`, `register_model` |

```yaml title="Montaje en docker-compose.yml"
volumes:
  - ./src:/opt/airflow/src   # Airflow worker
  - ./src:/home/src          # JupyterLab
  - ./src:/app/src           # FastAPI
```
