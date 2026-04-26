"""
DAG de disponibilidad de datos — disponibles desde MinIO.
"""

import datetime
import os
import boto3
from airflow.decorators import dag, task

BUCKET_NAME = "data-lake"
ARCHIVOS_S3 = ["aerolineas/train.csv", "aerolineas/test.csv"]
RUTA_DESTINO = "/opt/airflow/datasets/aerolineas"

default_args = {
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=5),
}


@dag(
    dag_id="descarga_datasets_desde_minio_v2",
    description="Descarga de datasets a MinIO",
    start_date=datetime.datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["import", "datasets", "boto3"],
    default_args=default_args,
)
def import_and_process_pipeline():

    @task(task_id="tarea_descarga_minio")
    def download_from_s3():
        s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT_URL', 'http://minio:9000'),
            aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
            region_name='us-east-1'
        )

        if not os.path.exists(RUTA_DESTINO):
            os.makedirs(RUTA_DESTINO, exist_ok=True)
        
        for key in ARCHIVOS_S3:
            local_file_path = os.path.join(RUTA_DESTINO, os.path.basename(key))
            print(f"Descargando {key} desde {BUCKET_NAME}...")
            
            s3_client.download_file(BUCKET_NAME, key, local_file_path)
            print(f"Archivo guardado en: {local_file_path}")

    download_from_s3()

dag_instancia = import_and_process_pipeline()