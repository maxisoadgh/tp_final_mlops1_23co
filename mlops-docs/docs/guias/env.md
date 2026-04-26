# Variables de entorno

Copiar `.env.example` a `.env` antes de levantar el stack. El `.env` está en `.gitignore`.

```bash
cp .env.example .env
```

## Referencia completa

| Variable | Default | Descripción |
|----------|---------|-------------|
| `PG_USER` | `postgres` | Usuario PostgreSQL |
| `PG_PASSWORD` | `postgres` | Password PostgreSQL |
| `PG_PORT` | `5432` | Puerto PostgreSQL |
| `MINIO_ACCESS_KEY` | `minio` | Access key MinIO |
| `MINIO_SECRET_ACCESS_KEY` | `minio123` | Secret key MinIO |
| `MINIO_PORT` | `9000` | Puerto API MinIO |
| `MINIO_PORT_UI` | `9001` | Puerto Console MinIO |
| `MLFLOW_BUCKET_NAME` | `mlflow` | Bucket de artefactos |
| `MLFLOW_PORT` | `5000` | Puerto MLflow |
| `JUPYTER_PORT` | `8888` | Puerto JupyterLab |
| `API_PORT` | `8000` | Puerto FastAPI |
| `STREAMLIT_PORT` | `8501` | Puerto Streamlit |
| `AIRFLOW_PORT` | `8080` | Puerto Airflow |
| `AIRFLOW_UID` | `50000` | UID proceso Airflow |
| `AIRFLOW_IMAGE_NAME` | `extending_airflow:latest` | Imagen Airflow custom |
| `AIRFLOW_PG_USER` | `airflow` | Usuario BD Airflow |
| `AIRFLOW_PG_PASSWORD` | `airflow` | Password BD Airflow |
| `AIRFLOW_PG_DATABASE` | `airflow` | Nombre BD Airflow |
| `_AIRFLOW_WWW_USER_USERNAME` | `airflow` | Usuario UI Airflow |
| `_AIRFLOW_WWW_USER_PASSWORD` | `airflow` | Password UI Airflow |
| `AIRFLOW__API_AUTH__JWT_SECRET` | — | **Cambiar en producción** |
