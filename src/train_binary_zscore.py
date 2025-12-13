import pandas as pd
import numpy as np
import pickle
import os
import re
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODEL_DIR = "src/models"
os.makedirs(MODEL_DIR, exist_ok=True)

# PARSE FUNCTIONS

def parse_ccm(val):
    txt = str(val)
    m = re.findall(r"(\d+)-(\d+)", txt)
    if m:
        a, b = map(int, m[0])
        return (a + b) / 2
    m = re.findall(r"(\d+)", txt)
    return int(m[0]) if m else np.nan

def parse_hp(val):
    txt = str(val)
    m = re.findall(r"(\d+)-(\d+)", txt)
    if m:
        a, b = map(int, m[0])
        return (a + b) / 2
    m = re.findall(r"(\d+)", txt)
    return int(m[0]) if m else np.nan

# LOAD DATA

df = pd.read_csv("../data/raw/turkey_car_market.csv")

df["CCM"] = df["CCM"].apply(parse_ccm)
df["Beygir Gucu"] = df["Beygir Gucu"].apply(parse_hp)

CURRENT_YEAR = 2025
df["car_age"] = CURRENT_YEAR - df["Model Yıl"]
df["car_age"] = df["car_age"].clip(lower=1)
df["km_per_year"] = df["Km"] / df["car_age"]

num_features = [
    "CCM",
    "Beygir Gucu",
    "Km",
    "Model Yıl",
    "car_age",
    "km_per_year"
]
cat_features = [
    "Marka",
    "Yakıt Turu",
    "Vites",
    "Kasa Tipi",
    "Kimden",
    "Durum",
    "Arac Tip"
]

df[num_features] = df[num_features].fillna(df[num_features].median())

for col in cat_features:
    df[col] = df[col].astype("category")

# 1) PRICE REGRESSION

reg_features = num_features + cat_features
X_reg = df[reg_features]
y_reg = df["Fiyat"]

Xr_train, Xr_test, yr_train, yr_test = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

reg_model = LGBMRegressor(
    n_estimators=600,
    learning_rate=0.03,
    max_depth=12,
    num_leaves=50,
    subsample=0.9,
    colsample_bytree=0.8,
    verbosity=-1
)

reg_model.fit(
    Xr_train,
    yr_train,
    categorical_feature=cat_features
)

df["predicted_price"] = reg_model.predict(X_reg)

# PRICE / PERFORMANCE (AYNI)
df["price_perf"] = df["Fiyat"] / df["predicted_price"]
df["perf_z"] = (df["price_perf"] - df["price_perf"].mean()) / df["price_perf"].std()

df["label"] = 0
df.loc[df["perf_z"] <= 0.0, "label"] = 1

print("\nLABEL DISTRIBUTION:")
print(df["label"].value_counts(normalize=True))

# 3) CLASSIFICATION
X = df[reg_features]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LGBMClassifier(
    n_estimators=500,
    learning_rate=0.03,
    max_depth=10,
    num_leaves=40,
    subsample=0.9,
    colsample_bytree=0.8,
    class_weight="balanced",
    verbosity=-1
)

model.fit(
    X_train,
    y_train,
    categorical_feature=cat_features
)

preds = model.predict(X_test)

print("\n---- UPDATED PRICE/PERFORMANCE MODEL ----")
print("Accuracy:", accuracy_score(y_test, preds))
print(classification_report(y_test, preds))
print("Confusion Matrix:\n", confusion_matrix(y_test, preds))

# SAVE
pickle.dump(model, open(f"{MODEL_DIR}/binary_zscore_model.pkl", "wb"))
pickle.dump(reg_features, open(f"{MODEL_DIR}/binary_zscore_features.pkl", "wb"))
pickle.dump(reg_model, open(f"{MODEL_DIR}/price_regressor.pkl", "wb"))

print("\nModel saved successfully!")
