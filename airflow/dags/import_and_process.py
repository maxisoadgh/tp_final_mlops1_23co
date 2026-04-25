"""
DAG de disponibilidad de datos — disponibles desde MinIO.
"""

import datetime
import os
from airflow.decorators import dag, task

CONN_ID = "minio_conn"
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
    description="Descarga de datasets desde MinIO usando TaskFlow API",
    start_date=datetime.datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["import", "datasets"],
)
def import_and_process_pipeline():

    @task(task_id="tarea_descarga_minio")
    def download_from_s3():
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

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

    download_from_s3()


dag_instancia = import_and_process_pipeline()
