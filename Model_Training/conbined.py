from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np

subtrainLabel = pd.read_csv('/malware_class/subtrain_label.csv')
subtrainfeature1 = pd.read_csv("/malware_class/3gramfeature.csv")
subtrainfeature2 = pd.read_csv("/malware_class/imgfeature.csv")
subtrain = pd.merge(subtrainfeature1, subtrainfeature2, on='Id')

labels = subtrain.Class
subtrain.drop(["Class", "Id"], axis=1, inplace=True)
subtrain = subtrain.iloc[:, :].values
srf = RF(n_estimators=500, n_jobs=-1)
clf_s = cross_val_score(srf, subtrain, labels, cv=10)
