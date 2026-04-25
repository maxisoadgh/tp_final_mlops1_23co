# TP — Aprendizaje de Máquina II

Entorno de desarrollo con Docker Compose para el trabajo práctico del curso.

## Integrantes

- Federica Pavese (federica.pavese@gmail.com)
- Liliana Mariel Di Lanzo (lic.dilanzo@gmail.com)
- Pablo A. Salvagni (psalvagni@gmail.com )
- Pablo Maximiliano Lulic (maxisoad@gmail.com)

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
├── docker-compose.yml
├── .env / .env.example
│
├── src/                                # módulos Python compartidos (montado en Airflow, API, Jupyter)
│   ├── config.py                       # constantes, columnas, paths
│   ├── data_loader.py                  # carga CSV, limpieza, get_dummies
│   ├── preprocessing.py                # ColumnTransformer, Pipeline, inferencia
│   ├── training.py                     # entrenamiento con Optuna + MLflow
│   ├── evaluation.py                   # métricas, selección y registro del mejor modelo
│   └── mlflow_utils.py                 # setup experimentos, registro en Model Registry
│
├── api/
│   ├── main.py                         # API de inferencia (FastAPI)
│   ├── schemas.py                      # modelos Pydantic (input/output)
│   └── requirements.txt
│
├── airflow/
│   ├── dags/
│   │   └── airline_satisfaction_dag.py # DAG de entrenamiento (TaskFlow API)
│   ├── logs/
│   ├── plugins/
│   ├── config/
│   └── secrets/
│       ├── connections.yaml
│       └── variables.yaml
│
├── notebooks/
│   ├── mlflow_hyperparam_search.ipynb  # búsqueda de hiperparámetros original
│   └── ...
│
├── datasets/
│   └── aerolineas/
│       ├── train.csv
│       └── test.csv
│
├── dockerfiles/
│   ├── jupyter/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── api/
│   │   └── Dockerfile
│   ├── mlflow/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── airflow/
│       ├── Dockerfile
│       └── requirements.txt
│
├── nginx/
│   └── mlflow.conf                     # proxy que reescribe Host header hacia MLflow
│
└── postgres/
    └── init.sql                        # crea bases airflow y mlflow_db
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
docker-compose up --build
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

Detener, eliminar volúmenes y las imágenes locales:

```bash
docker-compose down -v --rmi local
```

## Agregar paquetes Python al entorno Jupyter

Editar `dockerfiles/jupyter/requirements.txt` y hacer el build de nuevo:

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

Para agregar paquetes nuevos a la API, agregarlos en `api/requirements.txt` y hacer el build:

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
