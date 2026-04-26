# Predicción de Satisfacción de Pasajeros — MLOps I

## Integrantes

| Nombre | Email |
|---|---|
| Federica Pavese | federica.pavese@gmail.com |
| Liliana Mariel Di Lanzo | lic.dilanzo@gmail.com |
| Pablo A. Salvagni | psalvagni@gmail.com |
| Pablo Maximiliano Lulic | maxisoad@gmail.com |

---

## Problema de negocio

Las aerolíneas operan en un mercado altamente competitivo donde la experiencia del pasajero es un diferenciador clave. Cada vuelo genera una gran cantidad de interacciones —check-in, servicio a bordo, puntualidad, confort— y la percepción que el pasajero se lleva de ese conjunto determina si volverá a elegir la aerolínea o no.
El problema central es que la insatisfacción generalmente se detecta tarde: cuando ya llegó el reclamo, la reseña negativa, o simplemente cuando el pasajero no volvió a comprar.

### ¿Qué resuelve este proyecto?

Un modelo de clasificación binaria que predice, a partir de datos de encuesta, si un pasajero quedará:

- ✅ `satisfied` → cliente fidelizable, experiencia positiva
- ⚠️ `neutral or dissatisfied` → cliente en riesgo de abandono o generador de mala reputación

Si la aerolínea puede predecir qué perfil de pasajero tiene mayor probabilidad de insatisfacción, puede actuar de forma proactiva antes de que el daño esté hecho.

### Impacto concreto

| Área | Impacto |
|---|---|
| **Fidelización** | Identificar clientes en riesgo permite intervenciones a tiempo (upgrades, compensaciones, seguimiento post-vuelo) |
| **Reputación de marca** | Reducir la tasa de insatisfacción protege la imagen pública en plataformas como Google, TripAdvisor y redes sociales |
| **Segmentación operativa** | Las variables más predictivas permiten orientar inversiones de mejora de servicio hacia los segmentos más críticos |
| **Decisiones anticipadas** | En producción, el modelo puede ejecutarse cruzando datos del pasajero con información del servicio antes o durante el vuelo |

---

## Dataset

- **Fuente**: [Airline Passenger Satisfaction — Kaggle](https://www.kaggle.com/datasets/teejmahal20/airline-passenger-satisfaction)
- **Descripción**: Respuestas de encuestas sobre la satisfacción de pasajeros.
- **Split**: El dataset ya viene dividido en `train` y `test`, ubicados en `datasets/aerolineas/`.
- **Variable objetivo**: `satisfaction` → `{ neutral or dissatisfied: 0, satisfied: 1 }`
- **Limpieza**: Se eliminan ~0.3% de filas con valores nulos en `Arrival Delay in Minutes`. La columna `id` es descartada.

### Columnas del dataset

| Tipo | Columnas | Escalado |
|---|---|---|
| **Categóricas** | `Gender`, `Customer Type`, `Type of Travel`, `Class` | One-hot encoding (`drop_first=True`) |
| **Numéricas** | `Age`, `Flight Distance`, `Departure Delay in Minutes`, `Arrival Delay in Minutes` | `StandardScaler` |
| **Ratings 1–5** | `Inflight wifi service`, `Ease of Online booking`, `Food and drink`, `Seat comfort`, `Inflight entertainment`, `On-board service`, `Leg room service`, `Baggage handling`, `Checkin service`, `Cleanliness`, y más | `MinMaxScaler` |

---

## Estructura del repositorio

```
tp_final_mlops1_23co/
│
├── src/                               # Módulos Python reutilizables
│   ├── config.py                      # Columnas, constantes, experiment name
│   ├── data_loader.py                 # Carga de CSV y encoding del target
│   ├── preprocessing.py               # ColumnTransformer, pipelines sklearn
│   ├── training.py                    # Entrenamiento, tuning y logging de métricas/artifacts en MLflow
│   ├── evaluation.py                  # Métricas, figuras de evaluación y selección del mejor modelo
│   └── mlflow_utils.py                # Setup de experimentos y Model Registry
│
├── airflow/
│   ├── dags/
│   │   ├── import_and_process.py          # DAG de descarga y preparación inicial de datasets desde MinIO
│   │   └── airline_satisfaction_dag.py    # DAG principal de entrenamiento
│   ├── secrets/
│   │   ├── connections.yaml           # Conexiones S3/MinIO, bases de datos, etc.
│   │   └── variables.yaml             # Variables accesibles desde los DAGs
│   └── config/
│
├── notebooks/
│   ├── models.ipynb                   # Exploración de modelos
│   ├── mlflow_hyperparam_search.ipynb # Búsqueda de hiperparámetros con MLflow
│   └── test.ipynb
│
├── api/
│   ├── main.py                        # FastAPI app
│   └── requirements.txt
│
├── streamlit/
│   ├── streamlit_app.py               # Frontend Streamlit para consumir la API
│   └── .streamlit/
│       └── config.toml                # Tema visual de la app
│
├── dockerfiles/
│   ├── airflow/
│   │   ├── Dockerfile                 # apache/airflow:3.0.2 con dependencias extra
│   │   └── requirements.txt
│   ├── api/
│   │   └── Dockerfile                 # python:3.12-slim + uvicorn
│   ├── streamlit/
│   │   ├── Dockerfile                 # python:3.12-slim + Streamlit
│   │   └── requirements.txt
│   ├── jupyter/
│   │   ├── Dockerfile                 # python:3.12-slim + JupyterLab
│   │   └── requirements.txt
│   └── mlflow/
│       ├── Dockerfile
│       └── requirements.txt
│
├── datasets/
│   └── aerolineas/
│       ├── train.csv
│       └── test.csv
│
├── postgres/
│   └── init.sql                       # Crea las bases airflow y mlflow_db
│
├── nginx/
│   └── mlflow.conf                    # Proxy para resolver DNS rebinding check de MLflow
│
├── docker-compose.yml
└── .env.example
```

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Modelado | Python, scikit-learn, XGBoost |
| Optimización de hiperparámetros | Optuna (runs anidados en MLflow) |
| Experiment tracking | MLflow + PostgreSQL backend + MinIO artifact store |
| Serving / API | FastAPI + uvicorn |
| Frontend | Streamlit |
| Orquestación | Apache Airflow 3.0 (CeleryExecutor + Redis/Valkey) |
| Containerización | Docker / docker-compose |
| Object storage | MinIO (compatible S3) |
| Base de datos | PostgreSQL 14 |
| Proxy | nginx |

---

## Puesta en marcha

### Requisitos previos

- Docker Engine >= 24
- Docker Compose plugin >= 2.20
- Al menos **4 GB de RAM** y **2 CPUs** disponibles para Docker (requerimiento de Airflow)

### 1. Clonar el repositorio

```bash
git clone https://github.com/lilidl-nft/tp_final_mlops1_23co.git
cd tp_final_mlops1_23co
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si se quieren cambiar puertos o credenciales
```

El `.env` está excluido del repo porque contiene secretos. Variables clave:

```env
# PostgreSQL
PG_USER=postgres
PG_PASSWORD=postgres
PG_PORT=5432

# MinIO
MINIO_ACCESS_KEY=minio
MINIO_SECRET_ACCESS_KEY=minio123
MINIO_PORT=9000
MINIO_PORT_UI=9001

# MLflow
MLFLOW_PORT=5000
MLFLOW_BUCKET_NAME=mlflow

# JupyterLab
JUPYTER_PORT=8888

# FastAPI
API_PORT=8000

# Streamlit
STREAMLIT_PORT=8501

# Airflow
AIRFLOW__API_AUTH__JWT_SECRET=cambiar_este_valor_por_uno_seguro
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
AIRFLOW_PORT=8080
```

### 3. Levantar todos los servicios

```bash
docker-compose up --build
```

### 4. Verificar el estado

```bash
docker-compose ps
```

### 5. Ver logs de un servicio

```bash
docker-compose logs -f jupyter
docker-compose logs -f mlflow
docker-compose logs -f airflow-apiserver
```

### Detener el entorno

```bash
# Solo detener
docker-compose down

# Detener y eliminar volúmenes e imágenes locales
docker-compose down -v --rmi local
```

---

## Servicios disponibles

| Servicio | URL | Credenciales | Notas |
|---|---|---|---|
| **JupyterLab** | http://localhost:8888 | sin token/password | Notebooks en `/notebooks` |
| **FastAPI** | http://localhost:8000 | — | Docs en `/docs` y `/redoc` |
| **Streamlit** | http://localhost:8501 | — | Frontend para consultar predicciones |
| **MLflow UI** | http://localhost:5000 | — | Acceso externo directo |
| **mlflow-proxy** | interno `:5001` | — | Usado por Jupyter y Airflow internamente |
| **Airflow UI** | http://localhost:8080 | `airflow` / `airflow` | |
| **MinIO Console** | http://localhost:9001 | `minio` / `minio123` | |
| **MinIO API** | http://localhost:9000 | `minio` / `minio123` | |
| **PostgreSQL** | `localhost:5432` | `postgres` / `postgres` | |

---

## Tutorial: flujo completo de uso

Una vez que todos los contenedores están levantados y saludables, el flujo completo es el siguiente.

### Paso 1 — Descargar y preparar datasets desde MinIO

1. Abrir la UI de Airflow en http://localhost:8080 (`airflow` / `airflow`)
2. En la lista de DAGs, buscar **`descarga_datasets_desde_minio_v2`**
3. Activar el DAG con el toggle si aparece en pausa
4. Hacer click en **Trigger DAG ▶** (columna Actions)

Este DAG ejecuta la preparación inicial de los datos necesarios para el pipeline. Descarga o sincroniza los archivos requeridos desde MinIO y deja los datasets disponibles para que el DAG de entrenamiento pueda consumirlos.

El DAG debe finalizar correctamente antes de lanzar `airline_satisfaction_training`.

### Paso 2 — Lanzar el entrenamiento desde Airflow

Una vez completado `descarga_datasets_desde_minio_v2`, lanzar el DAG de entrenamiento.

1. En la lista de DAGs, buscar **`airline_satisfaction_training`**
2. Activar el DAG con el toggle si aparece en pausa
3. Hacer click en **Trigger DAG ▶** (columna Actions)

El DAG lanza las siguientes tasks:

```
load_and_prepare_data
        │
        ├──── train_logistic_regression ──┐
        ├──── train_knn ──────────────────┤
        ├──── train_random_forest ────────┤
        └──── train_xgboost ─────────────┘
                                          │
                               select_and_register_best
```

Los 4 modelos se entrenan en paralelo. Cada uno ejecuta una búsqueda de hiperparámetros con Optuna (`N_TRIALS = 10` por defecto). Al finalizar, `select_and_register_best` compara los F1-scores y registra el ganador en el MLflow Model Registry como `airline-satisfaction-best`.

> Para cambiar la cantidad de trials, editar la variable `N_TRIALS` en `airflow/dags/airline_satisfaction_dag.py`.

### Paso 3 — Monitorear el entrenamiento

**Desde Airflow:**
- Click en el DAG run activo para ver el grafo de tasks en tiempo real
- Click en cualquier task → **Logs** para ver el output detallado, incluyendo el F1 de cada modelo al finalizar

**Desde MLflow** (http://localhost:5000):
- En **Experiments**, seleccionar `airline-satisfaction`
- Se listan los runs de cada modelo. Expandir cualquiera para ver los runs anidados de cada trial de Optuna con sus hiperparámetros y métricas
- En **Models**, bajo `airline-satisfaction-best`, aparece la versión registrada del mejor modelo con su `run_id` de origen

### Paso 4 — Probar la inferencia desde Swagger o Streamlit

Una vez finalizado el DAG, la API ya tiene acceso al modelo registrado en MLflow.

**Opción A: Swagger / FastAPI**

1. Abrir http://localhost:8000/docs
2. Buscar el endpoint `POST /predict`
3. Hacer click en **Try it out** e ingresar un payload de ejemplo:

```json
{
  "Gender": "Male",
  "Customer Type": "Loyal Customer",
  "Age": 35,
  "Type of Travel": "Business travel",
  "Class": "Business",
  "Flight Distance": 1200,
  "Inflight wifi service": 4,
  "Departure/Arrival time convenient": 3,
  "Ease of Online booking": 4,
  "Gate location": 3,
  "Food and drink": 4,
  "Online boarding": 5,
  "Seat comfort": 5,
  "Inflight entertainment": 4,
  "On-board service": 4,
  "Leg room service": 4,
  "Baggage handling": 4,
  "Checkin service": 4,
  "Inflight service": 5,
  "Cleanliness": 4,
  "Departure Delay in Minutes": 0,
  "Arrival Delay in Minutes": 0
}
```

4. Ejecutar y verificar la respuesta con la predicción (`satisfied` / `neutral or dissatisfied`) y la probabilidad.

También se puede usar `curl` directamente:

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{...}'
```

**Opción B: Streamlit**

1. Abrir http://localhost:8501
2. Completar el formulario con los datos del pasajero o cargar el ejemplo precargado
3. Ejecutar la predicción desde la interfaz

El contenedor de Streamlit consume la API internamente usando `API_BASE_URL=http://api:8000`, definido en `docker-compose.yml`.

### Paso 5 — Reentrenar

Para lanzar un nuevo ciclo de entrenamiento (por ejemplo, con más trials o con datos actualizados), simplemente volver al Paso 1 y hacer Trigger DAG nuevamente. Cada ejecución genera un nuevo run en MLflow y, si el nuevo modelo supera al anterior, se registra una versión nueva en el Model Registry.

---

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
│         │                         │                     │
│  ┌──────────────┐       ┌──────────────┐                │
│  │  PostgreSQL  │       │  Redis/Valkey│                │
│  │  (airflow)   │       │  (broker)    │                │
│  └──────────────┘       └──────────────┘                │
└─────────────────────────────────────────────────────────┘
```

**Notas:**
- **PostgreSQL** tiene dos bases de datos: `airflow` (metadata de Airflow) y `mlflow_db` (backend store de MLflow). Ambas se crean automáticamente con `postgres/init.sql`.
- **MinIO** actúa como artifact store de MLflow (bucket `mlflow`) y como storage S3-compatible accesible desde DAGs y notebooks.
- **Airflow** usa CeleryExecutor con Redis/Valkey como broker de mensajes.

### Proxy nginx para MLflow

MLflow incluye una protección anti-DNS rebinding que rechaza requests cuyo header `Host` no sea `localhost` o `127.0.0.1`. Esto impide que otros contenedores se conecten directamente usando el nombre del servicio (`mlflow:5000`).

El servicio `mlflow-proxy` (nginx) resuelve esto interceptando las requests y reescribiendo el header antes de forwardearlas:

```
JupyterLab / Airflow → mlflow-proxy:5001 (nginx reescribe Host) → mlflow:5000
```

La variable `MLFLOW_TRACKING_URI` en Jupyter y Airflow apunta a `http://mlflow-proxy:5001` automáticamente — no hace falta llamar a `mlflow.set_tracking_uri()` desde los notebooks o DAGs.

---

## Módulos Python (`src/`)

### `config.py`
Centraliza todas las constantes del proyecto: nombres de columnas por tipo, nombre del experimento MLflow (`airline-satisfaction`) y nombre del modelo registrado (`airline-satisfaction-best`).

### `data_loader.py`
- `load_dataset(path)`: lee CSV, elimina columna `id` y filas nulas en `Arrival Delay in Minutes`.
- `prepare_features_target(df)`: separa features y target, aplica one-hot encoding con `pd.get_dummies(..., drop_first=True)`.

### `preprocessing.py`
- `build_preprocessor()`: construye un `ColumnTransformer` con `StandardScaler` para numéricas y `MinMaxScaler` para ratings.
- `prepare_single_prediction()`: convierte un dict de features a un DataFrame alineado con las columnas que el modelo espera (usado en la API para inferencia).

### `training.py`
Funciones de entrenamiento para Logistic Regression, KNN, Random Forest y XGBoost, integradas con Optuna + MLflow. Loguea métricas finales de test, métricas de tuning y artifacts visuales por modelo en MLflow; además usa `mlflow.start_run(nested=True)` para que cada trial de Optuna sea un run hijo visible en la UI.

### `evaluation.py`
- `compute_metrics()`: calcula precision, recall, F1 y accuracy.
- funciones para construir figuras de evaluación para MLflow: confusion matrix, ROC, Precision-Recall, feature importance y logistic coefficients.
- `select_best_run()`: selecciona el resultado con mayor F1.
- `register_best_model()`: combina selección y registro en el Model Registry.

### `mlflow_utils.py`
- `setup_experiment()`: crea el experimento si no existe y lo activa (lee `MLFLOW_TRACKING_URI` desde env vars).
- `log_feature_columns()`: loguea la lista de columnas como artefacto JSON (necesario para alinear features en inferencia).
- `register_model()`: registra un run en el Model Registry y retorna la versión generada.

---

## Modelos

El pipeline entrena y compara 4 modelos de clasificación. Todos usan **Optuna** para búsqueda de hiperparámetros con runs anidados trackeados en MLflow. El ganador por F1-score se registra automáticamente en el **MLflow Model Registry**.

| Modelo | Preprocesamiento | Hiperparámetros buscados |
|---|---|---|
| **Regresión Logística** | StandardScaler + MinMaxScaler (Pipeline) | `C` (via `LogisticRegressionCV`, cv=10) |
| **KNN** | StandardScaler + MinMaxScaler | `n_neighbors`, `weights`, `p` |
| **Random Forest** | Ninguno (invariante a escala) | `n_estimators`, `criterion`, `max_depth`, `min_samples_split`, `min_samples_leaf` |
| **XGBoost** | Ninguno | `n_estimators`, `max_depth`, `learning_rate`, `gamma`, `subsample`, `colsample_bytree`, L1/L2 |

XGBoost además usa early stopping con split interno 80/20 y `MedianPruner` de Optuna para descartar trials poco prometedores antes de tiempo.

Los resultados varían en cada ejecución según los trials de Optuna. Para ver el ranking actualizado de cada run, consultar la UI de MLflow en http://localhost:5000.

---

## Operaciones frecuentes

### Agregar un nuevo DAG

Copiar el archivo `.py` en `airflow/dags/`. Se detecta automáticamente sin reiniciar.

### Personalizar variables y conexiones de Airflow

Editar los archivos en `airflow/secrets/`:
- `connections.yaml`: conexiones a bases de datos, APIs, S3, etc.
- `variables.yaml`: variables accesibles desde los DAGs con `Variable.get("nombre")`

Los cambios se aplican sin reiniciar los contenedores.

### Agregar paquetes Python al entorno Jupyter

Editar `dockerfiles/jupyter/requirements.txt` y hacer rebuild:

```bash
docker-compose build jupyter
docker-compose up -d jupyter
```

### Agregar paquetes a la API

Editar `api/requirements.txt` y hacer rebuild:

```bash
docker-compose up --build -d api
```

### Agregar paquetes a Streamlit

Editar `dockerfiles/streamlit/requirements.txt` y hacer rebuild:

```bash
docker-compose up --build -d streamlit
```
