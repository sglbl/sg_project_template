"""Model training, hyperparameter optimization with Optuna, and experiment tracking pipeline."""

import joblib
from pathlib import Path
from typing import Any, Optional, Tuple
from loguru import logger
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from src.config import settings
from src.domain.models.ml_entities import ModelMetadata, ModelStage
from src.domain.repo_interfaces.tracker_repository import ITrackerRepository


class ModelTrainingPipeline:
    """Orchestrates model training, tuning, and logging to tracker."""

    def __init__(self, tracker: Optional[ITrackerRepository] = None) -> None:
        self.tracker = tracker
        self.artifacts_dir = Path(settings.MODEL_ARTIFACTS_DIR)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def tune_hyperparameters(
        self,
        x_train: pd.DataFrame,
        y_train: pd.Series,
        n_trials: int = 10,
    ) -> dict[str, Any]:
        """Run Optuna study to find optimal hyperparameters."""
        logger.info(f"Starting Optuna hyperparameter study with {n_trials} trials...")

        def objective(trial: optuna.Trial) -> float:
            n_estimators = trial.suggest_int("n_estimators", 20, 150)
            max_depth = trial.suggest_int("max_depth", 3, 15)
            min_samples_split = trial.suggest_int("min_samples_split", 2, 10)

            clf = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                random_state=42,
            )
            # 3-fold simple CV
            split_idx = int(len(x_train) * 0.75)
            clf.fit(x_train.iloc[:split_idx], y_train.iloc[:split_idx])
            val_preds = clf.predict(x_train.iloc[split_idx:])
            return float(accuracy_score(y_train.iloc[split_idx:], val_preds))

        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        best_params = study.best_params
        logger.info(f"Optuna tuning completed. Best Accuracy: {study.best_value:.4f} with params: {best_params}")
        return best_params

    def train_and_evaluate(
        self,
        train_path: str,
        test_path: str,
        target_col: str,
        model_name: str = "baseline_model",
        tune: bool = False,
        close_run: bool = True,
    ) -> Tuple[str, ModelMetadata]:
        """Train model, evaluate metrics, log to tracker, and persist binary artifact."""
        train_df = pd.read_parquet(train_path)
        test_df = pd.read_parquet(test_path)

        x_train = train_df.drop(columns=[target_col])
        y_train = train_df[target_col]
        x_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]

        # Hyperparameter selection
        params: dict[str, Any] = {
            "n_estimators": 50,
            "max_depth": 8,
            "random_state": 42,
        }
        if tune:
            best_params = self.tune_hyperparameters(x_train, y_train, n_trials=10)
            params.update(best_params)

        # Start tracking run
        if self.tracker:
            run_suffix = "optuna" if tune else "baseline"
            run_name = f"train_{model_name}_{run_suffix}"
            run_tags = {
                "tuning": "optuna" if tune else "baseline",
                "model_type": "RandomForest",
            }
            self.tracker.start_run(run_name=run_name, tags=run_tags)
            self.tracker.log_params(params)

        # Train model
        logger.info(f"Training RandomForest model '{model_name}'...")
        clf = RandomForestClassifier(**params)
        clf.fit(x_train, y_train)

        # Evaluation metrics
        y_pred = clf.predict(x_test)
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        }
        logger.info(f"Evaluation metrics: {metrics}")

        if self.tracker:
            self.tracker.log_metrics(metrics)

        # Save model binary (.pkl)
        model_file = self.artifacts_dir / f"{model_name}.pkl"
        joblib.dump({"model": clf, "features": list(x_train.columns), "target": target_col}, model_file)
        logger.info(f"Saved trained model binary to {model_file}")

        if self.tracker:
            self.tracker.log_artifact(str(model_file))
            if close_run:
                self.tracker.end_run()

        metadata = ModelMetadata(
            name=model_name,
            version="1.0.0",
            stage=ModelStage.DEVELOPMENT,
            metrics=metrics,
            parameters=params,
            artifact_path=str(model_file),
            framework="scikit-learn",
        )
        return str(model_file), metadata
