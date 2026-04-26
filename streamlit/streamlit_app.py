"""Frontend Streamlit para consumir la API de prediccion."""

import os
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

EXAMPLE_PAYLOAD = {
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


def get_api_health() -> dict:
    """Consulta el estado de la API."""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"status": "error", "model_loaded": False, "detail": str(exc)}


def predict_passenger(payload: dict) -> dict:
    """Envía una predicción a la API."""
    response = requests.post(PREDICT_URL, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def render_probability_bar(probability: float) -> None:
    """Renderiza una barra custom de probabilidad."""
    percentage = max(0.0, min(probability * 100, 100.0))
    st.markdown(
        f"""
        <div style="margin: 0.5rem 0 1rem 0;">
            <div style="
                background-color: #e5e7eb;
                border-radius: 999px;
                height: 18px;
                overflow: hidden;
            ">
                <div style="
                    width: {percentage:.2f}%;
                    background-color: #2563eb;
                    height: 100%;
                    border-radius: 999px;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_payload(use_example: bool) -> dict:
    """Construye el payload desde el formulario o desde el ejemplo."""
    defaults = EXAMPLE_PAYLOAD if use_example else {}

    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox(
            "Género",
            ["Male", "Female"],
            index=["Male", "Female"].index(defaults.get("gender", "Male")),
        )
        customer_type = st.selectbox(
            "Cliente",
            ["Loyal Customer", "disloyal Customer"],
            index=["Loyal Customer", "disloyal Customer"].index(
                defaults.get("customer_type", "Loyal Customer")
            ),
        )
        age = st.number_input(
            "Edad",
            min_value=0,
            max_value=120,
            value=defaults.get("age", 35),
            step=1,
        )
        type_of_travel = st.selectbox(
            "Viaje",
            ["Business travel", "Personal Travel"],
            index=["Business travel", "Personal Travel"].index(
                defaults.get("type_of_travel", "Business travel")
            ),
        )
        travel_class = st.selectbox(
            "Clase",
            ["Business", "Eco", "Eco Plus"],
            index=["Business", "Eco", "Eco Plus"].index(
                defaults.get("travel_class", "Business")
            ),
        )
        flight_distance = st.number_input(
            "Distancia",
            min_value=0,
            value=defaults.get("flight_distance", 1500),
            step=50,
        )

    with col2:
        inflight_wifi_service = st.slider(
            "Wifi", 0, 5, defaults.get("inflight_wifi_service", 4)
        )
        departure_arrival_time_convenient = st.slider(
            "Horario",
            0,
            5,
            defaults.get("departure_arrival_time_convenient", 4),
        )
        ease_of_online_booking = st.slider(
            "Reserva", 0, 5, defaults.get("ease_of_online_booking", 3)
        )
        gate_location = st.slider(
            "Puerta", 0, 5, defaults.get("gate_location", 3)
        )
        food_and_drink = st.slider(
            "Comida", 0, 5, defaults.get("food_and_drink", 4)
        )
        online_boarding = st.slider("Embarque", 0, 5, defaults.get("online_boarding", 5))
        cleanliness = st.slider("Limpieza", 0, 5, defaults.get("cleanliness", 4))
        departure_delay_in_minutes = st.number_input(
            "Delay salida",
            min_value=0,
            value=defaults.get("departure_delay_in_minutes", 0),
            step=5,
        )

    with col3:
        seat_comfort = st.slider("Asiento", 0, 5, defaults.get("seat_comfort", 4))
        inflight_entertainment = st.slider(
            "Entretenimiento a bordo",
            0,
            5,
            defaults.get("inflight_entertainment", 5),
        )
        on_board_service = st.slider(
            "A bordo", 0, 5, defaults.get("on_board_service", 4)
        )
        leg_room_service = st.slider(
            "Piernas", 0, 5, defaults.get("leg_room_service", 4)
        )
        baggage_handling = st.slider(
            "Equipaje", 0, 5, defaults.get("baggage_handling", 5)
        )
        checkin_service = st.slider(
            "Check-in", 0, 5, defaults.get("checkin_service", 4)
        )
        inflight_service = st.slider("Servicio", 0, 5, defaults.get("inflight_service", 4))
        arrival_delay_in_minutes = st.number_input(
            "Delay llegada",
            min_value=0.0,
            value=float(defaults.get("arrival_delay_in_minutes", 0.0)),
            step=5.0,
        )
    return {
        "gender": gender,
        "customer_type": customer_type,
        "age": int(age),
        "type_of_travel": type_of_travel,
        "travel_class": travel_class,
        "flight_distance": int(flight_distance),
        "inflight_wifi_service": inflight_wifi_service,
        "departure_arrival_time_convenient": departure_arrival_time_convenient,
        "ease_of_online_booking": ease_of_online_booking,
        "gate_location": gate_location,
        "food_and_drink": food_and_drink,
        "online_boarding": online_boarding,
        "seat_comfort": seat_comfort,
        "inflight_entertainment": inflight_entertainment,
        "on_board_service": on_board_service,
        "leg_room_service": leg_room_service,
        "baggage_handling": baggage_handling,
        "checkin_service": checkin_service,
        "inflight_service": inflight_service,
        "cleanliness": cleanliness,
        "departure_delay_in_minutes": int(departure_delay_in_minutes),
        "arrival_delay_in_minutes": float(arrival_delay_in_minutes),
    }


def main() -> None:
    """Renderiza la aplicación Streamlit."""
    st.set_page_config(
        page_title="Airline Satisfaction Predictor",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0.5rem;
            }
            h1 {
                margin-bottom: 0.1rem !important;
            }
            div[data-testid="stMetric"] {
                padding-top: 0.1rem;
            }
            div[data-baseweb="select"] > div {
                border-color: #2563eb !important;
            }
            div[data-baseweb="input"] > div {
                border-color: #2563eb !important;
            }
            div[data-baseweb="base-input"] > div {
                border-color: #2563eb !important;
            }
            div[data-testid="stNumberInput"] > div > div {
                border: 1px solid #2563eb !important;
                border-radius: 0.5rem !important;
            }
            div[data-testid="stNumberInput"] div[data-baseweb="input"] {
                border: 1px solid #2563eb !important;
                border-radius: 0.5rem !important;
                box-shadow: none !important;
            }
            div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
                border: 1px solid #2563eb !important;
                border-radius: 0.5rem !important;
                box-shadow: none !important;
            }
            div[data-testid="stNumberInput"] div[data-baseweb="input"] > div,
            div[data-testid="stNumberInput"] div[data-baseweb="base-input"] > div {
                border: none !important;
                box-shadow: none !important;
            }
            div[data-testid="stNumberInput"] input {
                border: none !important;
                box-shadow: none !important;
            }
            div[data-testid="stNumberInput"] button {
                color: #2563eb !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Airline Satisfaction Predictor")
    st.caption("Prediccion de satisfaccion usando la API del proyecto.")

    with st.sidebar:
        st.header("API")
        st.code(API_BASE_URL)
        health = get_api_health()
        if health.get("status") == "ok":
            if health.get("model_loaded"):
                st.success("API disponible y modelo cargado")
            else:
                st.warning("API disponible pero sin modelo cargado")
        else:
            st.error("No se pudo conectar con la API")
            if "detail" in health:
                st.caption(health["detail"])

        use_example = st.checkbox("Cargar ejemplo", value=True)

    result = None
    with st.form("prediction_form"):
        form_col, result_col = st.columns([3.2, 1.15], gap="large")
        with form_col:
            payload = build_payload(use_example)
        with result_col:
            st.subheader("Prediccion")
            st.caption("Ejecutá la consulta y mirá el resultado acá.")
            result_slot = st.container()
            submitted = st.form_submit_button("Predecir", use_container_width=True)

        with result_slot:
            if not submitted:
                st.info("Completá el formulario y presioná Predecir.")
            else:
                try:
                    result = predict_passenger(payload)
                except requests.HTTPError as exc:
                    detail = exc.response.text if exc.response is not None else str(exc)
                    st.error("La API devolvió un error.")
                    st.code(detail)
                except requests.RequestException as exc:
                    st.error("No se pudo conectar con la API.")
                    st.code(str(exc))
                else:
                    st.success("Predicción obtenida")
                    prediction_text = result["prediction"]
                    prediction_color = (
                        "#22c55e"
                        if prediction_text == "satisfied"
                        else "#ef4444"
                    )
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 0.75rem;">
                            <div style="font-size: 0.9rem; color: #94a3b8;">
                                Predicción
                            </div>
                            <div style="font-size: 1.35rem; font-weight: 700; color: {prediction_color};">
                                {prediction_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.metric(
                        "Probabilidad",
                        f"{result['probability_satisfied']:.2%}",
                    )
                    st.metric("Versión", result["model_version"])
                    render_probability_bar(float(result["probability_satisfied"]))
                    if st.form_submit_button(
                        "Nueva predicción",
                        use_container_width=True,
                    ):
                        st.rerun()

    if result is None:
        return

    debug_col1, debug_col2 = st.columns(2)
    with debug_col1:
        with st.expander("Payload"):
            st.json(payload)
    with debug_col2:
        with st.expander("Respuesta API"):
            st.json(result)


if __name__ == "__main__":
    main()
