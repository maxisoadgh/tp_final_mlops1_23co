"""Entrenamiento de modelos con Optuna y MLflow."""

import warnings

import mlflow
import mlflow.sklearn
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.config import NUMERIC_COLS, RANDOM_STATE
from src.mlflow_utils import log_feature_columns
from src.preprocessing import build_preprocessor, get_rating_cols

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)


def _start_nested_run(parent_run_id: str, name: str):
    """
    Abre un run hijo anidado dentro del run padre activo.
    Se ve mejor en MLFlow.
    """
    return mlflow.start_run(run_name=name, nested=True)


def train_logistic_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Entrena LogisticRegressionCV con Pipeline (preprocessor + modelo)."""
    rating_cols = get_rating_cols(X_train)
    preprocessor = build_preprocessor(NUMERIC_COLS, rating_cols)

    mlflow.sklearn.autolog(log_models=True, silent=True)
    try:
        with mlflow.start_run(
            run_name="LogisticRegression",
            tags={"model": "logistic_regression"},
        ) as run:
            pipe = Pipeline([
                ("pre", preprocessor),
                ("cls", LogisticRegressionCV(
                    cv=10, max_iter=1000,
                    random_state=RANDOM_STATE, n_jobs=-1,
                )),
            ])
            pipe.fit(X_train, y_train)

            y_pred = pipe.predict(X_test)
            test_f1 = f1_score(y_test, y_pred)
            mlflow.log_metric("test_f1", test_f1)
            log_feature_columns(list(X_train.columns))

            return {
                "run_id": run.info.run_id,
                "f1_score": round(test_f1, 4),
                "model_name": "logistic_regression",
            }
    finally:
        mlflow.sklearn.autolog(disable=True)


def train_knn(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_trials: int = 30,
) -> dict:
    """
    Entrena KNN con Optuna. Aplica preprocessor antes porque KNN
    si es sensible a la escala.

    :param n_trials: Cantidad de trials de Optuna
    :type n_trials: int
    """
    rating_cols = get_rating_cols(X_train)
    preprocessor = build_preprocessor(NUMERIC_COLS, rating_cols)

    pre_pipe = Pipeline([("pre", preprocessor)])
    X_train_scaled = pre_pipe.fit_transform(X_train)
    X_test_scaled = pre_pipe.transform(X_test)

    with mlflow.start_run(
        run_name="KNN", tags={"model": "knn"}
    ) as parent_run:
        parent_id = parent_run.info.run_id

        def objective(trial):
            params = {
                "n_neighbors": trial.suggest_int("n_neighbors", 1, 50),
                "weights": trial.suggest_categorical(
                    "weights", ["uniform", "distance"]
                ),
                "p": trial.suggest_int("p", 1, 2),
            }
            with _start_nested_run(parent_id, f"trial_{trial.number}"):
                mlflow.log_params(params)
                model = KNeighborsClassifier(**params, n_jobs=-1)
                score = cross_val_score(
                    model, X_train_scaled, y_train,
                    scoring="f1", cv=3, n_jobs=-1,
                ).mean()
                mlflow.log_metric("f1_cv", score)
            return score

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_f1", study.best_value)

        best_model = KNeighborsClassifier(
            **study.best_params, n_jobs=-1
        ).fit(X_train_scaled, y_train)
        mlflow.sklearn.log_model(best_model, "model")

        y_pred = best_model.predict(X_test_scaled)
        test_f1 = f1_score(y_test, y_pred)
        mlflow.log_metric("test_f1", test_f1)
        log_feature_columns(list(X_train.columns))

        return {
            "run_id": parent_id,
            "f1_score": round(test_f1, 4),
            "model_name": "knn",
        }


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_trials: int = 30,
) -> dict:
    """
    Entrena Random Forest con Optuna. Sin preprocessor (arboles no requieren scaling).

    :param n_trials: Cantidad de trials de Optuna
    :type n_trials: int
    """
    with mlflow.start_run(
        run_name="RandomForest", tags={"model": "random_forest"}
    ) as parent_run:
        parent_id = parent_run.info.run_id

        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 400),
                "criterion": trial.suggest_categorical(
                    "criterion", ["gini", "entropy"]
                ),
                "max_depth": trial.suggest_int("max_depth", 3, 30),
                "min_samples_split": trial.suggest_int(
                    "min_samples_split", 2, 20
                ),
                "min_samples_leaf": trial.suggest_int(
                    "min_samples_leaf", 1, 20
                ),
            }
            with _start_nested_run(parent_id, f"trial_{trial.number}"):
                mlflow.log_params(params)
                model = RandomForestClassifier(
                    **params, random_state=RANDOM_STATE, n_jobs=-1
                )
                score = cross_val_score(
                    model, X_train, y_train,
                    scoring="f1", cv=3, n_jobs=-1,
                ).mean()
                mlflow.log_metric("f1_cv", score)
            return score

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_f1", study.best_value)

        best_model = RandomForestClassifier(
            **study.best_params, random_state=RANDOM_STATE, n_jobs=-1
        )
        best_model.fit(X_train, y_train)
        mlflow.sklearn.log_model(best_model, "model")

        y_pred = best_model.predict(X_test)
        test_f1 = f1_score(y_test, y_pred)
        mlflow.log_metric("test_f1", test_f1)
        log_feature_columns(list(X_train.columns))

        return {
            "run_id": parent_id,
            "f1_score": round(test_f1, 4),
            "model_name": "random_forest",
        }


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_trials: int = 30,
) -> dict:
    """
    Entrena XGBoost con Optuna. Usa split interno 80/20 para early stopping.

    :param n_trials: Cantidad de trials de Optuna
    :type n_trials: int
    """
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=RANDOM_STATE
    )

    with mlflow.start_run(
        run_name="XGBoost", tags={"model": "xgboost"}
    ) as parent_run:
        parent_id = parent_run.info.run_id

        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 400),
                "max_depth": trial.suggest_int("max_depth", 2, 10),
                "grow_policy": trial.suggest_categorical(
                    "grow_policy", ["depthwise", "lossguide"]
                ),
                "learning_rate": trial.suggest_float(
                    "learning_rate", 1e-4, 1.0, log=True
                ),
                "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
                "min_child_weight": trial.suggest_int(
                    "min_child_weight", 1, 10
                ),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float(
                    "colsample_bytree", 0.5, 1.0
                ),
                "reg_alpha": trial.suggest_float(
                    "reg_alpha", 1e-8, 1.0, log=True
                ),
                "reg_lambda": trial.suggest_float(
                    "reg_lambda", 1e-8, 1.0, log=True
                ),
                "objective": "binary:logistic",
                "eval_metric": "auc",
                "device": "cpu",
                "tree_method": "hist",
                "random_state": RANDOM_STATE,
            }
            pruning_cb = optuna.integration.XGBoostPruningCallback(
                trial, "validation_0-auc"
            )

            with _start_nested_run(parent_id, f"trial_{trial.number}"):
                log_params = {
                    k: v for k, v in params.items()
                    if k not in (
                        "objective", "eval_metric", "device", "tree_method"
                    )
                }
                mlflow.log_params(log_params)

                model = XGBClassifier(
                    **params,
                    callbacks=[pruning_cb],
                    early_stopping_rounds=20,
                    verbosity=0,
                )
                model.fit(
                    X_tr, y_tr,
                    eval_set=[(X_val, y_val)],
                    verbose=False,
                )

                y_pred_val = model.predict(X_val)
                score = f1_score(y_val, y_pred_val)
                mlflow.log_metric("f1_cv", score)
            return score

        study = optuna.create_study(
            direction="maximize",
            pruner=optuna.pruners.MedianPruner(n_warmup_steps=5),
        )
        study.optimize(objective, n_trials=n_trials)

        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_f1", study.best_value)

        best_params = {
            **study.best_params,
            "objective": "binary:logistic",
            "device": "cpu",
            "tree_method": "hist",
        }
        best_model = XGBClassifier(
            **best_params, random_state=RANDOM_STATE, verbosity=0
        )
        best_model.fit(X_train, y_train)
        mlflow.sklearn.log_model(best_model, "model")

        y_pred = best_model.predict(X_test)
        test_f1 = f1_score(y_test, y_pred)
        mlflow.log_metric("test_f1", test_f1)
        log_feature_columns(list(X_train.columns))

        return {
            "run_id": parent_id,
            "f1_score": round(test_f1, 4),
            "model_name": "xgboost",
        }
