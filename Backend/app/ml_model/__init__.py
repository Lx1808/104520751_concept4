from .classification import load_model_components, predict_malware
from .prediction import load_prediction_model, predict_processor_usage

# 在这里加载模型,这样我们只需要加载一次
classification_model = load_model_components()
prediction_model, prediction_scaler = load_prediction_model()

# 读取hourly_data.csv文件
import pandas as pd
import os
from ..core.config import DATA_PATH

df_hourly = pd.read_csv(os.path.join(DATA_PATH, 'hourly_data.csv'), parse_dates=['ts'], index_col='ts')