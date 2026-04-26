# Pipeline de entrenamiento

Ver [Dataset & Modelo](index.md) para el diagrama completo del pipeline y la descripción de las columnas.

## Runs anidados en MLflow

Cada trial de Optuna se loguea como un **run anidado** dentro del run padre del modelo:

```
Run: XGBoost (padre)
  ├─ best_f1: 0.9543
  ├─ test_f1: 0.9543
  ├─ Run: trial_0 → f1_cv: 0.891, learning_rate: 0.05, n_estimators: 200...
  ├─ Run: trial_1 → f1_cv: 0.934, learning_rate: 0.12, n_estimators: 350...
  └─ ... (10 trials)
```

## Modelos candidatos

| Modelo | Librería | Scaling | Optuna | Notas |
|--------|---------|---------|--------|-------|
| `LogisticRegressionCV` | sklearn | `StandardScaler` + `MinMaxScaler` | No | CV=10 interno |
| `KNeighborsClassifier` | sklearn | Idem | Sí (10 trials) | Scaling previo a Optuna |
| `RandomForestClassifier` | sklearn | No | Sí (10 trials) | — |
| `XGBClassifier` | xgboost | No | Sí (10 trials) | MedianPruner + early stopping |
