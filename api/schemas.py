"""Esquemas Pydantic para la API de inferencia."""

from pydantic import BaseModel, Field


class PassengerFeatures(BaseModel):
    gender: str = Field(description="Genero del pasajero", examples=["Male"])
    customer_type: str = Field(description="Tipo de cliente", examples=["Loyal Customer"])
    age: int = Field(description="Edad del pasajero", ge=0, le=120)
    type_of_travel: str = Field(description="Proposito del viaje", examples=["Business travel"])
    travel_class: str = Field(description="Clase del ticket", examples=["Business"])
    flight_distance: int = Field(description="Distancia del vuelo en millas", ge=0)
    inflight_wifi_service: int = Field(description="Rating wifi a bordo (0-5)", ge=0, le=5)
    departure_arrival_time_convenient: int = Field(description="Rating conveniencia horario (0-5)", ge=0, le=5)
    ease_of_online_booking: int = Field(description="Rating reserva online (0-5)", ge=0, le=5)
    gate_location: int = Field(description="Rating ubicacion puerta (0-5)", ge=0, le=5)
    food_and_drink: int = Field(description="Rating comida y bebida (0-5)", ge=0, le=5)
    online_boarding: int = Field(description="Rating embarque online (0-5)", ge=0, le=5)
    seat_comfort: int = Field(description="Rating confort asiento (0-5)", ge=0, le=5)
    inflight_entertainment: int = Field(description="Rating entretenimiento (0-5)", ge=0, le=5)
    on_board_service: int = Field(description="Rating servicio a bordo (0-5)", ge=0, le=5)
    leg_room_service: int = Field(description="Rating espacio piernas (0-5)", ge=0, le=5)
    baggage_handling: int = Field(description="Rating manejo equipaje (0-5)", ge=0, le=5)
    checkin_service: int = Field(description="Rating check-in (0-5)", ge=0, le=5)
    inflight_service: int = Field(description="Rating servicio en vuelo (0-5)", ge=0, le=5)
    cleanliness: int = Field(description="Rating limpieza (0-5)", ge=0, le=5)
    departure_delay_in_minutes: int = Field(description="Retraso salida (min)", ge=0)
    arrival_delay_in_minutes: float = Field(description="Retraso llegada (min)", ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
                    "arrival_delay_in_minutes": 0.0,
                }
            ]
        }
    }


FIELD_TO_COLUMN = {
    "gender": "Gender",
    "customer_type": "Customer Type",
    "age": "Age",
    "type_of_travel": "Type of Travel",
    "travel_class": "Class",
    "flight_distance": "Flight Distance",
    "inflight_wifi_service": "Inflight wifi service",
    "departure_arrival_time_convenient": "Departure/Arrival time convenient",
    "ease_of_online_booking": "Ease of Online booking",
    "gate_location": "Gate location",
    "food_and_drink": "Food and drink",
    "online_boarding": "Online boarding",
    "seat_comfort": "Seat comfort",
    "inflight_entertainment": "Inflight entertainment",
    "on_board_service": "On-board service",
    "leg_room_service": "Leg room service",
    "baggage_handling": "Baggage handling",
    "checkin_service": "Checkin service",
    "inflight_service": "Inflight service",
    "cleanliness": "Cleanliness",
    "departure_delay_in_minutes": "Departure Delay in Minutes",
    "arrival_delay_in_minutes": "Arrival Delay in Minutes",
}


class PredictionResponse(BaseModel):
    prediction: str = Field(description="Nivel de satisfaccion predicho")
    probability_satisfied: float = Field(description="Probabilidad de satisfecho", ge=0, le=1)
    model_version: str = Field(description="Version del modelo en MLflow")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": "satisfied",
                    "probability_satisfied": 0.92,
                    "model_version": "1",
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    status: str = Field(description="Estado del servicio")
    model_loaded: bool = Field(description="Si el modelo esta cargado")


class APIInfo(BaseModel):
    name: str = "Airline Satisfaction Prediction API"
    description: str = "Prediccion de satisfaccion de pasajeros. Modelo entrenado con MLflow."
    version: str = "1.0.0"
