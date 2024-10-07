import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict
import json


class MalwareDetectionModel:
    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.models = {
            '4class': self.load_model(os.path.join(base_path, 'content', 'saved_model_4class')),
            'binary': self.load_model(os.path.join(base_path, 'content', 'saved_model_binary')),
            '16class': self.load_model(os.path.join(base_path, 'content', 'saved_model_16class'))
        }

    def load_model(self, model_path):
        with open(os.path.join(model_path, 'selected_features.json'), 'r') as f:
            feature_names = json.load(f)
        return {
            'scaler': joblib.load(os.path.join(model_path, 'scaler.joblib')),
            'base_models': [joblib.load(os.path.join(model_path, f'base_model_{i}.joblib')) for i in range(3)],
            'feature_names': feature_names
        }

    def predict(self, features: List[float]) -> Dict[str, any]:
        results = {}

        for model_name, model in self.models.items():
            X = pd.DataFrame([features], columns=model['feature_names'])
            X_scaled = model['scaler'].transform(X)
            X_scaled_df = pd.DataFrame(X_scaled, columns=model['feature_names'])

            predictions = [base_model.predict_proba(X_scaled_df)[:, 1] for base_model in model['base_models']]
            avg_prediction = float(np.mean(predictions))

            feature_values = {name: float(value) for name, value in zip(model['feature_names'], features)}

            results[model_name] = {
                "prediction": avg_prediction,
                "feature_values": feature_values
            }

        return results
