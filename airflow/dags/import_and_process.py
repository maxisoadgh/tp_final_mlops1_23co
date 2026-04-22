from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

CONN_ID = "minio_conn"
BUCKET_NAME = "datasets"


def descargar_de_minio():
    s3 = S3Hook(aws_conn_id=CONN_ID)

    archivos = ["train.csv", "val.csv"]
    ruta_destino = "/opt/airflow/datasets"

    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)

    for nombre_archivo in archivos:
        print(f"Buscando {nombre_archivo} en bucket {BUCKET_NAME}...")

        file_path = s3.download_file(
            key=nombre_archivo,
            bucket_name=BUCKET_NAME,
            local_path=ruta_destino,
            preserve_file_name=True,
        )
        print(f"Archivo {nombre_archivo} descargado exitosamente en: {file_path}")


with DAG(
    dag_id="descarga_datasets_desde_minio",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["tp_aprendizaje_maquina"],
) as dag:

    tarea_descarga = PythonOperator(
        task_id="tarea_descarga_minio", python_callable=descargar_de_minio
    )

dag = descargar_de_minio()
