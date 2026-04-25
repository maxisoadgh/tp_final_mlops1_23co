# `src/`

Este paquete concentra la lógica principal del proyecto: carga y preparación de datos, entrenamiento de modelos, evaluación, logging en MLflow y utilidades de soporte para inferencia y registro en Model Registry.

## Qué se registra en MLflow

El pipeline registra en MLflow métricas numéricas, modelos serializados y artifacts visuales para facilitar la comparación entre modelos, la interpretabilidad y la trazabilidad de las corridas.

### Métricas finales de test

Estas métricas se calculan sobre el conjunto de test del modelo final entrenado:

- `test_precision`: proporción de predicciones positivas que fueron correctas.
- `test_recall`: proporción de casos positivos reales que el modelo logró detectar.
- `test_f1`: media armónica entre precision y recall; es la métrica principal usada para comparar modelos al final del pipeline.
- `test_accuracy`: proporción total de predicciones correctas sobre el conjunto de test.

Estas cuatro métricas se registran para los cuatro modelos:

- Logistic Regression
- KNN
- Random Forest
- XGBoost

### Métricas de tuning

Durante la búsqueda de hiperparámetros, MLflow también registra métricas intermedias para evaluar cada trial.

Para KNN y Random Forest:

- `f1_cv`: promedio del F1 obtenido en validación cruzada.
- `f1_cv_std`: desvío estándar del F1 entre folds, usado para medir estabilidad del trial.
- `best_f1`: mejor valor de `f1_cv` encontrado por el estudio de Optuna.

Interpretación:

- `f1_cv` alto indica buen rendimiento promedio.
- `f1_cv_std` bajo indica comportamiento estable entre folds.

Para XGBoost:

- `val_f1`: F1 obtenido sobre un conjunto de validación interno usado durante cada trial.
- `best_f1`: mejor valor de `val_f1` encontrado por el estudio.

En este caso no se usa cross-validation para cada trial, sino un split holdout; por eso la métrica intermedia se llama `val_f1` y no `f1_cv`.

Logistic Regression no registra métricas de tuning porque en este flujo no usa Optuna.

## Criterio de selección del mejor modelo

El mejor modelo se selecciona comparando el valor final de F1 sobre test. En otras palabras, la comparación final entre modelos se basa en `test_f1` y no en las métricas intermedias del tuning.

## Artifacts registrados en MLflow

Además de las métricas, el pipeline almacena artifacts que ayudan a interpretar el modelo y reproducir la inferencia.

Artifacts comunes a todos los modelos:

- `model`: modelo entrenado serializado.
- `feature_columns.json`: lista de columnas esperadas por el modelo; luego se reutiliza en la API para alinear correctamente la entrada.
- `plots/confusion_matrix.png`: matriz de confusión del modelo sobre test.
- `plots/roc_curve.png`: curva ROC del modelo.
- `plots/precision_recall_curve.png`: curva Precision-Recall del modelo.

Artifacts específicos por modelo:

- Logistic Regression:
  - `plots/logistic_coefficients.png`: gráfico de los coeficientes más relevantes del modelo.
- Random Forest:
  - `plots/feature_importance.png`: gráfico de importancia de variables.
- XGBoost:
  - `plots/feature_importance.png`: gráfico de importancia de variables.
- KNN:
  - no registra artifacts extra de interpretabilidad en esta versión.

## Resumen por modelo

| Modelo | Métricas finales de test | Métricas de tuning | Artifacts comunes | Artifacts específicos |
|---|---|---|---|---|
| Logistic Regression | `test_precision`, `test_recall`, `test_f1`, `test_accuracy` | No aplica | `model`, `feature_columns.json`, `plots/confusion_matrix.png`, `plots/roc_curve.png`, `plots/precision_recall_curve.png` | `plots/logistic_coefficients.png` |
| KNN | `test_precision`, `test_recall`, `test_f1`, `test_accuracy` | `f1_cv`, `f1_cv_std`, `best_f1` | `model`, `feature_columns.json`, `plots/confusion_matrix.png`, `plots/roc_curve.png`, `plots/precision_recall_curve.png` | No registra artifacts extra de interpretabilidad |
| Random Forest | `test_precision`, `test_recall`, `test_f1`, `test_accuracy` | `f1_cv`, `f1_cv_std`, `best_f1` | `model`, `feature_columns.json`, `plots/confusion_matrix.png`, `plots/roc_curve.png`, `plots/precision_recall_curve.png` | `plots/feature_importance.png` |
| XGBoost | `test_precision`, `test_recall`, `test_f1`, `test_accuracy` | `val_f1`, `best_f1` | `model`, `feature_columns.json`, `plots/confusion_matrix.png`, `plots/roc_curve.png`, `plots/precision_recall_curve.png` | `plots/feature_importance.png` |

## Módulos principales

- `training.py`: entrena los modelos, ejecuta el tuning cuando corresponde y registra métricas, modelos y artifacts en MLflow.
- `evaluation.py`: centraliza el cálculo de métricas y la construcción de figuras de evaluación e interpretabilidad.
- `mlflow_utils.py`: agrupa helpers para configurar experimentos, registrar modelos y persistir artifacts auxiliares.
- `preprocessing.py`: define el preprocesamiento y utilidades para alinear columnas en entrenamiento e inferencia.
- `data_loader.py`: carga datasets y separa features/target.
- `config.py`: concentra constantes y nombres globales del proyecto.
