# Agregar paquetes Python

Cada servicio tiene su propio `requirements.txt`.

## JupyterLab

```bash
# 1. Editar dockerfiles/jupyter/requirements.txt
# 2. Reconstruir:
docker compose build jupyter
docker compose up -d jupyter
```

## FastAPI

```bash
# 1. Editar api/requirements.txt
# 2. Reconstruir:
docker compose up --build -d api
```

## Airflow (todos los componentes)

```bash
# 1. Editar dockerfiles/airflow/requirements.txt
# 2. Reconstruir TODOS (comparten la misma imagen):
docker compose build
docker compose up -d
```

!!! warning "Imagen compartida"
    `apiserver`, `scheduler`, `worker`, `dag-processor` y `triggerer` usan la misma imagen `extending_airflow:latest`. Hay que rebuildar y reiniciar todos al cambiar las dependencias.
