# Red interna

Todos los servicios comparten la red `backend` (bridge). Se comunican usando el **nombre del servicio como hostname**.

## Tabla de conexiones

| Desde | Hacia | Host:Puerto | Propósito |
|-------|-------|-------------|-----------|
| JupyterLab | mlflow-proxy | `mlflow-proxy:5001` | Tracking MLflow |
| JupyterLab | MinIO | `minio:9000` | Leer/escribir artefactos |
| FastAPI | mlflow-proxy | `mlflow-proxy:5001` | Cargar modelo del Registry |
| FastAPI | MinIO | `minio:9000` | Descargar artefactos del modelo |
| Airflow worker | mlflow-proxy | `mlflow-proxy:5001` | Log de runs y artefactos |
| Airflow worker | MinIO | `minio:9000` | Guardar modelos y `feature_columns.json` |
| mlflow-proxy | MLflow | `mlflow:5000` | Forward con Host rewrite |
| MLflow | PostgreSQL | `postgres:5432` | Backend store (`mlflow_db`) |
| MLflow | MinIO | `minio:9000` | Artifact store (`s3://mlflow/`) |
| Airflow * | PostgreSQL | `postgres:5432` | Metadata (`airflow`) |
| Airflow * | Redis | `redis:6379` | Celery broker |

## Variables de entorno comunes

```bash
# En JupyterLab, FastAPI y Airflow worker:
MLFLOW_TRACKING_URI=http://mlflow-proxy:5001
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
AWS_ENDPOINT_URL_S3=http://minio:9000
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
```

## Conexión MinIO desde Airflow (secrets)

```yaml title="airflow/secrets/connections.yaml"
minio_conn:
  conn_type: aws
  login: ${MINIO_ACCESS_KEY}
  password: ${MINIO_SECRET_ACCESS_KEY}
  extra:
    endpoint_url: "http://minio:9000"
    region_name: "us-east-1"
```

!!! note "¿Por qué variables `AWS_*` para MinIO?"
    MinIO implementa la API S3 de AWS. MLflow usa boto3 para subir artefactos, y boto3 lee las variables `AWS_*`. Con `AWS_ENDPOINT_URL_S3` apuntando a MinIO, boto3 habla con MinIO en lugar de AWS S3 real.
