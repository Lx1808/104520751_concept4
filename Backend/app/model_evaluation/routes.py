from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from ..auth.utils import get_current_user
from ..ml_model import predict_malware, classification_model
import pandas as pd
import io
from sklearn.metrics import classification_report, confusion_matrix
import json

router = APIRouter()


@router.post("/evaluate-model")
async def evaluate_model(
        file: UploadFile = File(...),
        current_user: dict = Depends(get_current_user)
):
    if current_user['roles'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    # 读取上传的文件
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

    # 确保数据集包含所需的特征
    required_features = ["feature1", "feature2", "feature3"]  # 替换为实际的特征名
    if not all(feature in df.columns for feature in required_features):
        raise HTTPException(status_code=400, detail="Dataset missing required features")

    # 假设最后一列是真实标签
    true_labels = df.iloc[:, -1]
    features = df.iloc[:, :-1]

    # 使用模型进行预测
    predictions = predict_malware(features, classification_model)

    # 计算性能指标
    report = classification_report(true_labels, predictions, output_dict=True)
    conf_matrix = confusion_matrix(true_labels, predictions).tolist()

    return {
        "classification_report": report,
        "confusion_matrix": conf_matrix
    }