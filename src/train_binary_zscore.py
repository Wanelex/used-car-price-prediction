import pandas as pd
import numpy as np
import pickle
import os
import re
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score

MODEL_DIR = "src/models"
os.makedirs(MODEL_DIR, exist_ok=True)

CURRENT_YEAR = 2025

# Feature weights for health score calculation
FEATURE_WEIGHTS = {
    'age': 0.25,
    'km_per_year': 0.25,
    'total_km': 0.20,
    'model_year': 0.10,
    'hp': 0.10,
    'ccm': 0.10
}


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


def calculate_health_score(df, weights):
    """
    Calculate composite health score from 6 numerical features.
    Each feature is normalized to 0-1 range, then weighted.
    Higher score = better condition.
    """
    # Age score: newer is better (0-20 years range)
    age_score = np.clip(1 - (df['car_age'] / 20), 0, 1)

    # km_per_year score: lower usage is better (0-30000 km/year range)
    km_per_year_score = np.clip(1 - (df['km_per_year'] / 30000), 0, 1)

    # Total km score: lower mileage is better (0-400000 km range)
    km_score = np.clip(1 - (df['Km'] / 400000), 0, 1)

    # Model year score: more recent is better (1959-2025 range)
    year_score = (df['Model Yıl'] - 1959) / (CURRENT_YEAR - 1959)
    year_score = np.clip(year_score, 0, 1)

    # HP score: higher power is better (50-250 HP range)
    hp_score = np.clip((df['Beygir Gucu'] - 50) / 200, 0, 1)

    # CCM score: optimal around 1450cc, penalize extremes
    ccm_score = np.clip(1 - (np.abs(df['CCM'] - 1450) / 1000), 0, 1)

    # Composite weighted score
    health_score = (
        weights['age'] * age_score +
        weights['km_per_year'] * km_per_year_score +
        weights['total_km'] * km_score +
        weights['model_year'] * year_score +
        weights['hp'] * hp_score +
        weights['ccm'] * ccm_score
    )

    return health_score


# LOAD DATA
print("Loading data...")
df = pd.read_csv("data/raw/turkey_car_market.csv")
print(f"Loaded {len(df)} records")

# Parse numeric features
df["CCM"] = df["CCM"].apply(parse_ccm)
df["Beygir Gucu"] = df["Beygir Gucu"].apply(parse_hp)

# Create derived features
df["car_age"] = CURRENT_YEAR - df["Model Yıl"]
df["car_age"] = df["car_age"].clip(lower=1)
df["km_per_year"] = df["Km"] / df["car_age"]

# Define numerical features (only these 6, no categorical)
num_features = [
    "CCM",
    "Beygir Gucu",
    "Km",
    "Model Yıl",
    "car_age",
    "km_per_year"
]

# Check missing values before imputation
print("\nMissing values before imputation:")
for col in num_features:
    missing = df[col].isna().sum()
    pct = missing / len(df) * 100
    print(f"  {col}: {missing} ({pct:.1f}%)")

# Handle missing values with Iterative Imputer
print("\nApplying Iterative Imputer for missing values...")
imputer = IterativeImputer(max_iter=10, random_state=42)
df[num_features] = imputer.fit_transform(df[num_features])

# Calculate health score for each car
print("\nCalculating health scores...")
df['health_score'] = calculate_health_score(df, FEATURE_WEIGHTS)

# Analyze health score distribution
print("\nHealth Score Statistics:")
print(df['health_score'].describe())

# Create binary labels based on 50th percentile
threshold = np.percentile(df['health_score'], 50)
df['label'] = (df['health_score'] >= threshold).astype(int)

print(f"\nLabel threshold (50th percentile): {threshold:.4f}")
print("\nLABEL DISTRIBUTION:")
print(df['label'].value_counts(normalize=True))

# Sanity check: compare feature means by label
print("\n=== SANITY CHECK: Feature means by label ===")
buyable = df[df['label'] == 1]
not_buyable = df[df['label'] == 0]

print(f"BUYABLE (label=1) avg car_age: {buyable['car_age'].mean():.1f} years")
print(f"NOT BUYABLE (label=0) avg car_age: {not_buyable['car_age'].mean():.1f} years")
print(f"BUYABLE avg km: {buyable['Km'].mean():,.0f} km")
print(f"NOT BUYABLE avg km: {not_buyable['Km'].mean():,.0f} km")
print(f"BUYABLE avg km/year: {buyable['km_per_year'].mean():,.0f} km/year")
print(f"NOT BUYABLE avg km/year: {not_buyable['km_per_year'].mean():,.0f} km/year")

# Prepare features and labels for training
X = df[num_features]
y = df['label']

# Train/test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# Train LightGBM classifier
print("\nTraining LightGBM classifier...")
model = LGBMClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    class_weight='balanced',
    random_state=42,
    verbosity=-1
)

model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
probs = model.predict_proba(X_test)[:, 1]

print("\n=== BUYABILITY PREDICTION MODEL (FEATURES ONLY) ===")
print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, probs):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, preds, target_names=['Not Buyable', 'Buyable']))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, preds))

# Cross-validation
print("\nPerforming 5-fold cross-validation...")
cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
print(f"Cross-Validation ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Feature importance
print("\nFeature Importances:")
importances = pd.DataFrame({
    'feature': num_features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(importances.to_string(index=False))

# Save model artifacts
print("\nSaving model artifacts...")
pickle.dump(model, open(f"{MODEL_DIR}/buyability_model.pkl", "wb"))
pickle.dump(imputer, open(f"{MODEL_DIR}/feature_imputer.pkl", "wb"))
pickle.dump(num_features, open(f"{MODEL_DIR}/buyability_features.pkl", "wb"))
pickle.dump(threshold, open(f"{MODEL_DIR}/health_threshold.pkl", "wb"))
pickle.dump(FEATURE_WEIGHTS, open(f"{MODEL_DIR}/feature_weights.pkl", "wb"))

print("\nModel artifacts saved:")
print(f"  - {MODEL_DIR}/buyability_model.pkl")
print(f"  - {MODEL_DIR}/feature_imputer.pkl")
print(f"  - {MODEL_DIR}/buyability_features.pkl")
print(f"  - {MODEL_DIR}/health_threshold.pkl")
print(f"  - {MODEL_DIR}/feature_weights.pkl")

print("\nModel training completed successfully!")
