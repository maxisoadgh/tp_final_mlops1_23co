# Agregar DAGs

Los DAGs se detectan automáticamente desde `airflow/dags/`. Copiar el archivo `.py` y el scheduler lo parsea en el siguiente ciclo.

## Estructura recomendada (TaskFlow API)

```python title="airflow/dags/mi_dag.py"
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id="mi_dag",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ml"],
)
def mi_pipeline():

    @task
    def mi_task():
        from src.config import EXPERIMENT_NAME  # src/ está en el PATH del worker
        # ...

    mi_task()

dag = mi_pipeline()
```

## Variables desde Airflow

```python
from airflow.models import Variable

model_name = Variable.get("registered_model_name",
                          default_var="airline-satisfaction-best")
```

Las variables están en `airflow/secrets/variables.yaml` y se aplican sin reiniciar.
