# MinIO — Object Storage

MinIO provee una API S3-compatible localmente. Se usa como artifact store de MLflow y como data lake para los datasets.

## Acceso

| Interfaz | URL | Usuario | Password |
|----------|-----|---------|----------|
| Console (UI) | <http://localhost:9001> | `minio` | `minio123` |
| API S3 | <http://localhost:9000> | `minio` | `minio123` |

---

## Buckets

| Bucket | Contenido | Creado por |
|--------|-----------|-----------|
| `mlflow` | Artefactos de MLflow (modelos, `feature_columns.json`) | `minio-create-buckets` al levantar |
| `data-lake` | Datasets CSV (`aerolineas/train.csv`, `aerolineas/test.csv`) | Manual o via DAG |

!!! warning "Bucket `data-lake`"
    El DAG `descarga_datasets_desde_minio_v2` espera encontrar los CSVs en `s3://data-lake/aerolineas/`. Si el bucket no existe o está vacío, el DAG falla. Crearlo desde la UI de MinIO y subir los archivos manualmente la primera vez.

---

## Estructura de artefactos en `mlflow`

```
s3://mlflow/
└── <experiment_id>/
    └── <run_id>/
        └── artifacts/
            ├── model/              # modelo serializado (sklearn/xgboost)
            └── feature_columns.json
```

---

## Acceso desde Python (notebooks)

```python
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",      # dentro del contenedor
    aws_access_key_id="minio",
    aws_secret_access_key="minio123",
)

for obj in s3.list_objects(Bucket="mlflow").get("Contents", []):
    print(obj["Key"])
```

!!! tip "Desde el host (fuera de Docker)"
    Reemplazá `http://minio:9000` por `http://localhost:9000`.
