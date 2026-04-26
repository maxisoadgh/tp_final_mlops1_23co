# Quickstart

## Prerequisitos

- Docker Engine ≥ 24
- Docker Compose plugin ≥ 2.20
- Al menos **4 GB de RAM** para Docker (requerimiento de Airflow)

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/maxisoadgh/tp_final_mlops1_23co
cd tp_final_mlops1_23co
```

---

## 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Los defaults del `.env.example` funcionan para desarrollo local sin cambios.

---

## 3. Levantar el stack

```bash
docker compose up --build
```

!!! warning "Primera vez"
    El primer arranque tarda varios minutos: se buildean las imágenes custom y Airflow inicializa su base de datos. Es normal ver mensajes de `connection refused` mientras los servicios arrancan.

---

## 4. Verificar estado

```bash
docker compose ps
```

Todos los servicios deben estar `running` (excepto `airflow-init` y `minio-create-buckets` que terminan con código 0).

---

## 5. Cargar datasets en MinIO

Antes de entrenar, subir los CSVs al bucket `data-lake`:

1. Ir a <http://localhost:9001> (MinIO Console)
2. Crear el bucket `data-lake`
3. Crear la carpeta `aerolineas/`
4. Subir `train.csv` y `test.csv`

O usar el DAG `descarga_datasets_desde_minio_v2` si ya están en MinIO.

---

## 6. Entrenar el modelo

1. Ir a <http://localhost:8080> (Airflow UI)
2. Activar y correr `airline_satisfaction_training`
3. Esperar ~10–20 min (depende del hardware)

---

## 7. Verificar la API

```bash
curl http://localhost:8000/health
# → {"status":"ok","model_loaded":true}

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"gender":"Male","customer_type":"Loyal Customer","age":35,
       "type_of_travel":"Business travel","travel_class":"Business",
       "flight_distance":1500,"inflight_wifi_service":4,
       "departure_arrival_time_convenient":4,"ease_of_online_booking":3,
       "gate_location":3,"food_and_drink":4,"online_boarding":5,
       "seat_comfort":4,"inflight_entertainment":5,"on_board_service":4,
       "leg_room_service":4,"baggage_handling":5,"checkin_service":4,
       "inflight_service":4,"cleanliness":4,
       "departure_delay_in_minutes":0,"arrival_delay_in_minutes":0.0}'
```

---

## URLs de acceso

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| FastAPI Swagger | <http://localhost:8000/docs> | — |
| MLflow | <http://localhost:5000> | — |
| Airflow | <http://localhost:8080> | `airflow` / `airflow` |
| MinIO Console | <http://localhost:9001> | `minio` / `minio123` |
| JupyterLab | <http://localhost:8888> | sin token |

---

## Comandos útiles

```bash
# Logs en tiempo real
docker compose logs -f api
docker compose logs -f mlflow
docker compose logs -f airflow-apiserver

# Reiniciar un servicio
docker compose restart api

# Bajar todo (preserva volúmenes)
docker compose down

# Bajar + eliminar volúmenes ⚠️
docker compose down -v --rmi local
```
