# JupyterLab

## Acceso

```
http://localhost:8888   (sin token ni password)
```

---

## Notebooks disponibles

| Notebook | Descripción |
|----------|-------------|
| `mlflow_hyperparam_search.ipynb` | Búsqueda de hiperparámetros con Optuna, logging en MLflow |
| `models.ipynb` | Análisis y comparación de modelos |
| `test.ipynb` | Pruebas y experimentos |

---

## Variables pre-configuradas

No hace falta configurar nada manualmente — todo viene de las variables de entorno del contenedor:

```bash
MLFLOW_TRACKING_URI=http://mlflow-proxy:5001
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
```

---

## Volúmenes montados

| Host | Contenedor | Descripción |
|------|-----------|-------------|
| `./notebooks/` | `/home/notebooks/` | Notebooks |
| `./datasets/` | `/home/datasets/` | Datasets CSV |
| `./src/` | `/home/src/` | Módulos Python compartidos |

---

## Paquetes disponibles

```
jupyterlab · pandas · numpy · scikit-learn
matplotlib · seaborn · mlflow[extras] · boto3
xgboost · optuna · optuna-integration[xgboost]
dython · ipywidgets
```

---

## Agregar paquetes

```bash
# 1. Agregar en dockerfiles/jupyter/requirements.txt
# 2. Reconstruir:
docker compose build jupyter
docker compose up -d jupyter
```
