"""
DAG de entrenamiento — satisfaccion de pasajeros de aerolineas.

Carga datos, entrena 4 modelos en paralelo con Optuna + MLflow,
y registra el mejor en el Model Registry.
"""

import datetime
import sys

sys.path.insert(0, "/opt/airflow")

from airflow.decorators import dag, task

default_args = {
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=5),
    "dagrun_timeout": datetime.timedelta(minutes=120),
}

# aca defino la cantidad de trials para todos los modelos
N_TRIALS = 10


@dag(
    dag_id="airline_satisfaction_training",
    description="Entrena 4 modelos con Optuna, registra el mejor en MLflow",
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=["ml", "training", "airline-satisfaction"],
)
def airline_satisfaction_pipeline():

    @task(task_id="load_and_prepare_data", multiple_outputs=True)
    def load_and_prepare_data() -> dict:
        """Descarga de MinIO/S3, preprocesa y prepara para el entrenamiento."""
        import os
        import uuid

        import pandas as pd

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        from src.config import EXPERIMENT_NAME
        from src.data_loader import load_dataset, prepare_features_target
        from src.mlflow_utils import setup_experiment

        setup_experiment(EXPERIMENT_NAME)

        s3 = S3Hook(aws_conn_id="minio_conn")
        BUCKET = "data-lake"
        LOCAL_DIR = "/opt/airflow/datasets/aerolineas"
        ARCHIVOS_S3 = ["aerolineas/train.csv", "aerolineas/test.csv"]

        os.makedirs(LOCAL_DIR, exist_ok=True)

        for key in ARCHIVOS_S3:
            s3.download_file(
                key=key,
                bucket_name=BUCKET,
                local_path=LOCAL_DIR,
                preserve_file_name=True,
            )

        os.makedirs(LOCAL_DIR, exist_ok=True)
        for key in ARCHIVOS_S3:
            s3.download_file(
                key=key,
                bucket_name=BUCKET,
                local_path=LOCAL_DIR,
                preserve_file_name=True,
            )

        df_train = load_dataset(os.path.join(LOCAL_DIR, "train.csv"))
        df_test = load_dataset(os.path.join(LOCAL_DIR, "test.csv"))

        X_train, y_train = prepare_features_target(df_train)
        X_test, y_test = prepare_features_target(df_test)

        run_dir = f"/tmp/airline_sat_{uuid.uuid4().hex[:8]}"
        os.makedirs(run_dir, exist_ok=True)

        X_train.to_parquet(os.path.join(run_dir, "X_train.parquet"))
        y_train.to_frame().to_parquet(os.path.join(run_dir, "y_train.parquet"))
        X_test.to_parquet(os.path.join(run_dir, "X_test.parquet"))
        y_test.to_frame().to_parquet(os.path.join(run_dir, "y_test.parquet"))

        return {"data_dir": run_dir}

    @task(task_id="train_logistic_regression")
    def train_lr_task(data_dir: str) -> dict:
        import pandas as pd
        from src.config import EXPERIMENT_NAME
        from src.mlflow_utils import setup_experiment
        from src.training import train_logistic_regression

        setup_experiment(EXPERIMENT_NAME)

        X_train = pd.read_parquet(f"{data_dir}/X_train.parquet")
        y_train = pd.read_parquet(f"{data_dir}/y_train.parquet").iloc[:, 0]
        X_test = pd.read_parquet(f"{data_dir}/X_test.parquet")
        y_test = pd.read_parquet(f"{data_dir}/y_test.parquet").iloc[:, 0]

        result = train_logistic_regression(X_train, y_train, X_test, y_test)
        print(f"LogReg -- F1: {result['f1_score']}")
        return result

    @task(task_id="train_knn")
    def train_knn_task(data_dir: str) -> dict:
        import pandas as pd
        from src.config import EXPERIMENT_NAME
        from src.mlflow_utils import setup_experiment
        from src.training import train_knn

        setup_experiment(EXPERIMENT_NAME)

        X_train = pd.read_parquet(f"{data_dir}/X_train.parquet")
        y_train = pd.read_parquet(f"{data_dir}/y_train.parquet").iloc[:, 0]
        X_test = pd.read_parquet(f"{data_dir}/X_test.parquet")
        y_test = pd.read_parquet(f"{data_dir}/y_test.parquet").iloc[:, 0]

        result = train_knn(X_train, y_train, X_test, y_test, n_trials=N_TRIALS)
        print(f"KNN -- F1: {result['f1_score']}")
        return result

    @task(task_id="train_random_forest")
    def train_rf_task(data_dir: str) -> dict:
        import pandas as pd
        from src.config import EXPERIMENT_NAME
        from src.mlflow_utils import setup_experiment
        from src.training import train_random_forest

        setup_experiment(EXPERIMENT_NAME)

        X_train = pd.read_parquet(f"{data_dir}/X_train.parquet")
        y_train = pd.read_parquet(f"{data_dir}/y_train.parquet").iloc[:, 0]
        X_test = pd.read_parquet(f"{data_dir}/X_test.parquet")
        y_test = pd.read_parquet(f"{data_dir}/y_test.parquet").iloc[:, 0]

        result = train_random_forest(
            X_train, y_train, X_test, y_test, n_trials=N_TRIALS
        )
        print(f"RandomForest -- F1: {result['f1_score']}")
        return result

    @task(task_id="train_xgboost")
    def train_xgb_task(data_dir: str) -> dict:
        import pandas as pd
        from src.config import EXPERIMENT_NAME
        from src.mlflow_utils import setup_experiment
        from src.training import train_xgboost

        setup_experiment(EXPERIMENT_NAME)

        X_train = pd.read_parquet(f"{data_dir}/X_train.parquet")
        y_train = pd.read_parquet(f"{data_dir}/y_train.parquet").iloc[:, 0]
        X_test = pd.read_parquet(f"{data_dir}/X_test.parquet")
        y_test = pd.read_parquet(f"{data_dir}/y_test.parquet").iloc[:, 0]

        result = train_xgboost(X_train, y_train, X_test, y_test, n_trials=N_TRIALS)
        print(f"XGBoost -- F1: {result['f1_score']}")
        return result

    @task(task_id="select_and_register_best")
    def select_and_register_best(
        lr_result: dict,
        knn_result: dict,
        rf_result: dict,
        xgb_result: dict,
    ) -> dict:
        from src.config import EXPERIMENT_NAME, REGISTERED_MODEL_NAME
        from src.evaluation import register_best_model
        from src.mlflow_utils import setup_experiment

        setup_experiment(EXPERIMENT_NAME)

        results = [lr_result, knn_result, rf_result, xgb_result]

        print("Resultados:")
        print(f"  {'Modelo':<25} {'F1':>8}")
        print("  " + "-" * 35)
        for r in sorted(results, key=lambda x: -x["f1_score"]):
            print(f"  {r['model_name']:<25} {r['f1_score']:>8.4f}")

        registered = register_best_model(results, REGISTERED_MODEL_NAME)

        print(f"\nMejor modelo: {registered['model_name']}")
        print(f"  F1: {registered['f1_score']}")
        print(f"  Registry: {REGISTERED_MODEL_NAME} v{registered['registry_version']}")

        return registered

    data = load_and_prepare_data()
    data_dir = data["data_dir"]

    lr = train_lr_task(data_dir)
    knn = train_knn_task(data_dir)
    rf = train_rf_task(data_dir)
    xgb = train_xgb_task(data_dir)

    select_and_register_best(lr, knn, rf, xgb)


dag = airline_satisfaction_pipeline()
