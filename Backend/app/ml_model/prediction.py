import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
import joblib
import matplotlib.pyplot as plt
import io
import base64
from ..core.config import SAVED_MODEL_PATH
import os


def load_prediction_model():
    from tensorflow.keras.utils import custom_object_scope

    model_path = os.path.join(SAVED_MODEL_PATH, 'lstm_model.h5')
    scaler_path = os.path.join(SAVED_MODEL_PATH, 'scaler.pkl')

    with custom_object_scope({'mse': MeanSquaredError()}):
        model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler


def predict_processor_usage(start_date: str, end_date: str, df_hourly: pd.DataFrame, model, scaler):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_data = df_hourly[start_date:end_date]

    if len(filtered_data) < 25:
        return {'error': 'Not enough data in the selected range. Please select a wider date range.'}

    scaled_data = scaler.transform(filtered_data['Processor_pct_ Processor_Time'].values.reshape(-1, 1))

    seq_length = 24
    X = []
    for i in range(len(scaled_data) - seq_length):
        X.append(scaled_data[i:(i + seq_length), 0])
    X = np.array(X)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    predictions = model.predict(X)
    predictions = scaler.inverse_transform(predictions)

    actual_values = filtered_data['Processor_pct_ Processor_Time'].iloc[seq_length:].values
    timestamps = filtered_data.index[seq_length:]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, actual_values, label='Actual', color='blue')
    plt.plot(timestamps, predictions, label='Predicted', color='red')
    plt.xlabel('Timestamp')
    plt.ylabel('Processor % Processor Time')
    plt.title('Hourly Average Processor Usage')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return {
        'plot': plot_data,
        'actual': actual_values.tolist(),
        'predicted': predictions.reshape(-1).tolist(),
        'timestamps': [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in timestamps]
    }