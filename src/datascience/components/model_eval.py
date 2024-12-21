import os
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn
import numpy as np
import joblib
from pathlib import Path
from src.datascience.entity.config_entity import (ModelEvalConfig)
from src.datascience.utils.common import save_json

import os
os.environ['MLFLOW_TRACKING_URI']="https://dagshub.com/rahulsamantcoc2/End-to-End_Flash_App.mlflow"
os.environ['MLFLOW_TRACKING_USERNAME']="rahulsamantcoc2"
os.environ['MLFLOW_TRACKING_PASSWORD']="33607bcb15d4e7a7cca29f0f443d16762cc15549"

class ModelEval:
    def __init__(self, config: ModelEvalConfig):
        self.config = config
    def Eval(self,actual,pred):
        """
        Calculate classification metrics
        
        Args:
            actual: True labels
            pred: Predicted labels
            
        Returns:
            tuple: (accuracy, precision, recall, f1)
        """
        accuracy = accuracy_score(actual, pred)
        precision, recall, f1, _ = precision_recall_fscore_support(actual, pred, average='weighted')
        return accuracy, precision, recall, f1
    
    def log_into_mlflow(self):

        test_data = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path)

        test_x = test_data.drop([self.config.target_column], axis=1)
        test_y = test_data[[self.config.target_column]]


        mlflow.set_registry_uri(self.config.mlflow_uri)
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run():
            # Make predictions
            predicted_labels = model.predict(test_x)

            # Calculate metrics
            accuracy, precision, recall, f1 = self.Eval(test_y, predicted_labels)
            
            # Generate detailed classification report
            class_report = classification_report(test_y, predicted_labels)
            
            # Save metrics locally
            scores = {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1)
            }
            save_json(path=Path(self.config.metric_file_name), data=scores)

            # Log parameters and metrics to MLflow
            mlflow.log_params(self.config.all_params)
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1)

            # Log classification report as a text artifact
            with open("classification_report.txt", "w") as f:
                f.write(class_report)
            mlflow.log_artifact("classification_report.txt")


            # Register model if not using file store
            if tracking_url_type_store != "file":
                mlflow.sklearn.log_model(model, "model", registered_model_name="IrisClassifier")
            else:
                mlflow.sklearn.log_model(model, "model")