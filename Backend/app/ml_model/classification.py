import os
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
import json
from sklearn.feature_selection import SelectKBest, f_classif
from ..core.config import SAVED_MODEL_PATH


def load_model_components():
    model_path = os.path.join(SAVED_MODEL_PATH, "saved_model_16class")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The directory {model_path} does not exist.")

    components = {}
    required_files = [
        "base_model_0.joblib", "base_model_1.joblib", "base_model_2.joblib",
        "meta_learner.keras", "le_16class.joblib", "scaler.joblib",
        "feature_selector.joblib", "variance_selector.joblib", "selected_features.json"
    ]

    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required file {file} not found in {model_path}")

        if file.endswith('.json'):
            with open(file_path, 'r') as f:
                components[file[:-5]] = json.load(f)
        elif file.endswith('.keras'):
            components[file[:-6]] = tf.keras.models.load_model(file_path)
        else:
            components[file[:-7]] = joblib.load(file_path)

    return components


def predict_malware(df: pd.DataFrame, model_components: dict):
    print("Initial shape:", df.shape)

    if df.shape[1] != 55:
        raise ValueError(f"Expected 55 features, but got {df.shape[1]}")

    df = df.apply(pd.to_numeric, errors='coerce')

    if df.isna().any().any():
        print("Warning: Some values could not be converted to numeric. These have been replaced with NaN.")
        df = df.fillna(0)

    X = df.values

    print("Features shape:", X.shape)

    X_var = model_components['variance_selector'].transform(X)
    print("Shape after variance thresholding:", X_var.shape)

    X_selected = model_components['feature_selector'].transform(X_var)
    print("Shape after feature selection:", X_selected.shape)

    X_scaled = model_components['scaler'].transform(X_selected)

    base_predictions = []
    for i in range(3):
        base_predictions.append(model_components[f'base_model_{i}'].predict_proba(X_scaled))

    meta_features = np.hstack(base_predictions)

    final_predictions = model_components['meta_learner'].predict(meta_features)
    predicted_classes = np.argmax(final_predictions, axis=1)

    predicted_labels = model_components['le_16class'].inverse_transform(predicted_classes)

    results = []
    for label, confidence in zip(predicted_labels, np.max(final_predictions, axis=1)):
        results.append({
            'Predicted Class': label,
            'Confidence': float(confidence)
        })

    return results