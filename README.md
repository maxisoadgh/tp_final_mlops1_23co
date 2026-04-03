# TP — Aprendizaje de Máquina II

Entorno de desarrollo con Docker Compose para el trabajo práctico del curso.

## Servicios

| Servicio      | URL                          | Credenciales          | Notas                          |
|---------------|------------------------------|-----------------------|--------------------------------|
| JupyterLab    | http://localhost:8888        | sin token/password    |                                |
| FastAPI       | http://localhost:8000        | —                     | docs en /docs                  |
| MLflow        | http://localhost:5000        | —                     | acceso externo directo         |
| mlflow-proxy  | interno :5001                | —                     | usado por Jupyter internamente |
| Airflow       | http://localhost:8080        | airflow / airflow     |                                |
| MinIO Console | http://localhost:9001        | minio / minio123      |                                |
| MinIO API     | http://localhost:9000        | minio / minio123      |                                |
| PostgreSQL    | localhost:5432               | postgres / postgres   |                                |

## Estructura del proyecto

```
TP/
├── docker-compose.yml              # definición de todos los servicios
├── .env                            # variables de entorno (puertos, credenciales) — no versionar
├── .env.example                    # plantilla de .env para compartir
├── .gitignore
├── requirements.txt                # paquetes Python del entorno JupyterLab
│
├── api/
│   ├── main.py                     # app FastAPI
│   └── requirements.txt
│
├── dockerfiles/
│   ├── jupyter/
│   │   └── Dockerfile              # python:3.12-slim + uv + JupyterLab
│   ├── api/
│   │   └── Dockerfile              # python:3.12-slim + uv + uvicorn
│   ├── mlflow/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── airflow/
│       ├── Dockerfile              # apache/airflow:3.0.2 con dependencias extra
│       └── requirements.txt
│
├── nginx/
│   └── mlflow.conf                 # proxy que reescribe Host header hacia MLflow
│
├── postgres/
│   └── init.sql                    # crea las bases de datos airflow y mlflow_db
│
├── notebooks/                      # directorio local montado en JupyterLab
│   └── (tus notebooks van aquí)
│
└── airflow/
    ├── dags/                       # DAGs de Airflow
    ├── logs/                       # logs generados por Airflow (ignorado en git)
    ├── plugins/                    # plugins personalizados
    ├── config/                     # configuración adicional
    └── secrets/
        ├── connections.yaml        # conexiones (ej: S3/MinIO, bases de datos)
        └── variables.yaml          # variables de entorno para los DAGs
```

## Requisitos previos

- Docker Engine >= 24
- Docker Compose plugin >= 2.20
- Al menos 4 GB de RAM disponibles para Docker (requerimiento de Airflow)

## Configuración inicial

Copiar `.env.example` a `.env` y ajustar los valores según entorno. El `.env` está excluido del repo porque tiene secretos.

```bash
cp .env.example .env
```

## Levantar el entorno

```bash
# Desde el directorio
docker-compose up --build -d
```

Ver el estado de los contenedores:

```bash
docker-compose ps
```

Ver los logs de un servicio:

```bash
docker-compose logs -f jupyter
docker-compose logs -f mlflow
docker-compose logs -f airflow-apiserver
```

Detener el entorno:

```bash
docker-compose down
```

Detener y eliminar volúmenes (borra datos de Postgres y MinIO):

```bash
docker-compose down -v
```

## Agregar paquetes Python al entorno Jupyter

Editar el `requirements.txt` de la raíz y hacer el build de nuevo:

```bash
docker-compose build jupyter
docker-compose up -d jupyter
```

## Arquitectura interna

Todos los servicios comparten la red interna `backend`. Las conexiones entre contenedores usan el nombre del servicio como hostname.

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  JupyterLab │────▶│ mlflow-proxy │────▶│    MLflow    │────▶│  PostgreSQL  │
│  :8888      │     │  nginx :5001 │     │    :5000     │     │  (mlflow_db) │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                  ▲                      │
       │                  │               ┌──────────────┐
       └──────────────────┼──────────────▶│    MinIO     │
                          │               │  :9000/:9001 │
┌─────────────┐           │               └──────────────┘
│   FastAPI   │───────────┘
│   :8000     │
└─────────────┘

┌─────────────────────────────────────────────────────────┐
│  Airflow (CeleryExecutor)                               │
│  apiserver :8080 · scheduler · dag-processor            │
│  worker · triggerer                                     │
│         │                   │                           │
│  ┌──────────────┐   ┌──────────────┐                    │
│  │  PostgreSQL  │   │  Redis       │                    │
│  │  (airflow)   │   │  (broker)    │                    │
│  └──────────────┘   └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

- **PostgreSQL** tiene dos bases de datos: `airflow` (metadata de Airflow) y `mlflow_db` (backend store de MLflow). Ambas se crean automáticamente al iniciar con `postgres/init.sql`.
- **MinIO** actúa como artifact store de MLflow (bucket `mlflow`) y como storage S3-compatible accesible desde DAGs y notebooks.
- **Airflow** usa CeleryExecutor con Redis/Valkey como broker de mensajes.

### Proxy nginx para MLflow - Workaround

MLflow incluye una protección anti-DNS rebinding que rechaza cualquier request cuyo header `Host` no sea `localhost` o `127.0.0.1`. Esto impide que otros contenedores se conecten directamente usando el nombre del servicio (`mlflow:5000`).

El servicio `mlflow-proxy` (nginx) resuelve esto interceptando las requests de Jupyter y reescribiendo el header `Host: localhost` antes de forwardearlas a MLflow:

```
JupyterLab → mlflow-proxy:5001 (nginx: Host → localhost) → mlflow:5000
```

La configuración está en `nginx/mlflow.conf`. La variable de entorno `MLFLOW_TRACKING_URI` en el contenedor Jupyter apunta a `http://mlflow-proxy:5001` automáticamente — no hace falta llamar a `mlflow.set_tracking_uri()` desde los notebooks.

## FastAPI

El código de la API está en `api/main.py`. Los cambios aplicados se ven automáticamente.

Para agregar paquetes nuevos a la API, agregarlos en `api/requirements.txt` y hacer el build:º

```bash
docker-compose up --build -d api
```

FastAPI genera documentación:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

La API tiene acceso a MLflow (vía proxy) y MinIO con las mismas variables de entorno que Jupyter.

## Uso desde notebooks

Las variables de entorno necesarias ya están configuradas en el contenedor de `jupyter`.

Hay un ejemplo que se llama test.py en la carpeta notebooks.

## Airflow — agregar DAGs

Copiar los DAGs en `airflow/dags/`. Se detectan automáticamente.

## Personalizar variables y conexiones de Airflow

Editar los archivos en `airflow/secrets/`:

- `connections.yaml`: conexiones a bases de datos, APIs, S3, etc.
- `variables.yaml`: variables accesibles desde los DAGs con `Variable.get("nombre")`

Los cambios se aplican sin reiniciar los contenedores.
