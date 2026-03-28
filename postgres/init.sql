-- Crea el usuario y base de datos para Airflow
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;

-- Crea la base de datos para MLflow (usa el superusuario postgres)
CREATE DATABASE mlflow_db OWNER postgres;
