# FastAPI — Serving de predicciones

Al arrancar, la API carga automáticamente la **última versión registrada** de `airline-satisfaction-best` desde el MLflow Model Registry.

## Acceso

| Interfaz | URL |
|----------|-----|
| Swagger UI | <http://localhost:8000/docs> |
| ReDoc | <http://localhost:8000/redoc> |

---

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| `GET` | `/` | Info de la API |
| `GET` | `/health` | Estado del servicio y si el modelo está cargado |
| `POST` | `/reload` | Recarga el modelo desde MLflow sin reiniciar |
| `POST` | `/predict` | Predice la satisfacción de un pasajero |

---

## POST /predict

### Features de entrada (22 campos)

=== "Categóricos"

    | Campo | Descripción | Ejemplo |
    |-------|-------------|---------|
    | `gender` | Género | `"Male"` / `"Female"` |
    | `customer_type` | Tipo de cliente | `"Loyal Customer"` / `"disloyal Customer"` |
    | `type_of_travel` | Propósito del viaje | `"Business travel"` / `"Personal Travel"` |
    | `travel_class` | Clase | `"Business"` / `"Eco"` / `"Eco Plus"` |

=== "Numéricos"

    | Campo | Tipo | Descripción |
    |-------|------|-------------|
    | `age` | `int` (0–120) | Edad |
    | `flight_distance` | `int` ≥ 0 | Distancia en millas |
    | `departure_delay_in_minutes` | `int` ≥ 0 | Retraso de salida |
    | `arrival_delay_in_minutes` | `float` ≥ 0 | Retraso de llegada |

=== "Ratings (0–5)"

    | Campo |
    |-------|
    | `inflight_wifi_service` |
    | `departure_arrival_time_convenient` |
    | `ease_of_online_booking` |
    | `gate_location` |
    | `food_and_drink` |
    | `online_boarding` |
    | `seat_comfort` |
    | `inflight_entertainment` |
    | `on_board_service` |
    | `leg_room_service` |
    | `baggage_handling` |
    | `checkin_service` |
    | `inflight_service` |
    | `cleanliness` |

### Ejemplo completo

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male",
    "customer_type": "Loyal Customer",
    "age": 35,
    "type_of_travel": "Business travel",
    "travel_class": "Business",
    "flight_distance": 1500,
    "inflight_wifi_service": 4,
    "departure_arrival_time_convenient": 4,
    "ease_of_online_booking": 3,
    "gate_location": 3,
    "food_and_drink": 4,
    "online_boarding": 5,
    "seat_comfort": 4,
    "inflight_entertainment": 5,
    "on_board_service": 4,
    "leg_room_service": 4,
    "baggage_handling": 5,
    "checkin_service": 4,
    "inflight_service": 4,
    "cleanliness": 4,
    "departure_delay_in_minutes": 0,
    "arrival_delay_in_minutes": 0.0
  }'
```

### Response `200 OK`

```json
{
  "prediction": "satisfied",
  "probability_satisfied": 0.9231,
  "model_version": "3"
}
```

| Campo | Descripción |
|-------|-------------|
| `prediction` | `"satisfied"` o `"neutral or dissatisfied"` |
| `probability_satisfied` | Probabilidad de la clase positiva (vía `predict_proba`) |
| `model_version` | Número de versión en MLflow Registry |

---

## GET /health

```json
{ "status": "ok", "model_loaded": true }
```

!!! warning "503 antes de correr el DAG"
    Si no hay ningún modelo registrado en MLflow, `/predict` retorna `503`:
    ```json
    { "detail": "Modelo no disponible. Ejecutar el DAG de entrenamiento antes." }
    ```

---

## POST /reload

Recarga el modelo sin reiniciar el contenedor. Útil después de que Airflow registra una nueva versión.

```bash
curl -X POST http://localhost:8000/reload
# → {"status": "model reloaded", "model_loaded": true}
```

---

## Lógica de carga del modelo

```python title="api/main.py — _load_model()"
client = mlflow.MlflowClient()
versions = client.search_model_versions(f"name='{REGISTERED_MODEL_NAME}'")
latest = sorted(versions, key=lambda v: int(v.version))[-1]  # (1)

model = mlflow.sklearn.load_model(f"runs:/{latest.run_id}/model")

local_path = client.download_artifacts(latest.run_id, "feature_columns.json")  # (2)
with open(local_path) as f:
    feature_columns = json.load(f)
```

1. Toma la versión con el número más alto.
2. Descarga `feature_columns.json` para garantizar que el preprocessing use exactamente las mismas columnas con las que se entrenó el modelo.

!!! tip "Workflow completo"
    ```
    DAG airline_satisfaction_training
        → MLflow Registry (nueva versión)
            → POST /reload
                → API usa el nuevo modelo
    ```
