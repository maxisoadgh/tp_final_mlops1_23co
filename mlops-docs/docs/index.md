# MLOps TP Final

<div class="hero" markdown>
<h1>✈️ Airline Satisfaction MLOps Platform</h1>
<p>Plataforma completa de entrenamiento, versionado y serving de modelos ML para predecir la satisfacción de pasajeros de aerolíneas.</p>
<div class="badges">
  <span class="badge">🐳 Docker Compose</span>
  <span class="badge">⚡ FastAPI</span>
  <span class="badge">📊 MLflow + MinIO</span>
  <span class="badge">🔄 Airflow 3.0 CeleryExecutor</span>
  <span class="badge">🔬 JupyterLab</span>
</div>
</div>

## ¿Qué hace este proyecto?

TP Final de la materia **MLops I**. Implementa un stack MLOps completo para predecir si un pasajero quedará **satisfecho** o **neutral/insatisfecho** con su vuelo.

El flujo completo cubre:

1. **Ingesta** de datos desde MinIO mediante el DAG `descarga_datasets_desde_minio_v2`
2. **Experimentación** en JupyterLab con búsqueda de hiperparámetros via Optuna
3. **Entrenamiento** paralelo de 4 modelos orquestado por Airflow (DAG `airline_satisfaction_training`)
4. **Tracking** de todos los runs en MLflow, con artefactos en MinIO (S3-compatible)
5. **Serving** en tiempo real vía FastAPI, cargando el modelo desde MLflow Model Registry

---

## Servicios

<div class="service-grid" markdown>
<div class="service-card" markdown>
<div class="icon">🔬</div>
**JupyterLab**

Exploración, EDA y experimentación. Pre-configurado con MLflow y MinIO.

[Ver docs →](servicios/jupyter.md)
</div>

<div class="service-card" markdown>
<div class="icon">⚡</div>
**FastAPI**

Serving en tiempo real. Carga el modelo desde MLflow Registry al arrancar.

[Ver docs →](servicios/api.md)
</div>

<div class="service-card" markdown>
<div class="icon">📊</div>
**MLflow**

Tracking de experimentos y Model Registry. Backend en PostgreSQL, artefactos en MinIO.

[Ver docs →](servicios/mlflow.md)
</div>

<div class="service-card" markdown>
<div class="icon">🪣</div>
**MinIO**

Object storage S3-compatible. Datasets en `data-lake`, modelos en `mlflow`.

[Ver docs →](servicios/minio.md)
</div>

<div class="service-card" markdown>
<div class="icon">🔄</div>
**Airflow 3.0**

DAGs de ingesta y entrenamiento con CeleryExecutor + Redis.

[Ver docs →](servicios/airflow.md)
</div>
</div>

---

## URLs de acceso

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| JupyterLab | <http://localhost:8888> | sin token |
| FastAPI Swagger | <http://localhost:8000/docs> | — |
| MLflow UI | <http://localhost:5000> | — |
| Airflow UI | <http://localhost:8080> | `airflow` / `airflow` |
| MinIO Console | <http://localhost:9001> | `minio` / `minio123` |

!!! tip "Inicio rápido"
    ```bash
    cp .env.example .env
    docker compose up --build
    ```
    Ver la [guía completa →](guias/quickstart.md)
