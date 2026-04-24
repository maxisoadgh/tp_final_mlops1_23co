from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

CONN_ID = "minio_conn"
BUCKET_NAME = "data-lake"
ARCHIVOS_S3 = ["train.csv", "test.csv"]
RUTA_DESTINO = "/opt/airflow/datasets"


def load_and_prepare_data():
    s3 = S3Hook(aws_conn_id=CONN_ID)

    if not os.path.exists(RUTA_DESTINO):
        os.makedirs(RUTA_DESTINO, exist_ok=True)

    for key in ARCHIVOS_S3:
        print(f"Buscando {key} en bucket {BUCKET_NAME}...")

        file_path = s3.download_file(
            key=key,
            bucket_name=BUCKET_NAME,
            local_path=RUTA_DESTINO,
            preserve_file_name=True,
        )
        print(f"Archivo {key} descargado exitosamente en: {file_path}")


with DAG(
    dag_id="descarga_datasets_desde_minio",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["tp_aprendizaje_maquina"],
) as dag:

    tarea_descarga = PythonOperator(
        task_id="tarea_descarga_minio", python_callable=load_and_prepare_data
    )
