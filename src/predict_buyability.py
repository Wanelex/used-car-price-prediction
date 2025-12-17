"""
Buyability Prediction Module

Predicts car buyability based on 6 numerical features only (no price).
Returns a risk score (0-100) where higher = safer to buy.
"""
import pickle
import pandas as pd
import numpy as np
import re

MODEL_DIR = "src/models"
CURRENT_YEAR = 2025

# Load model artifacts
classifier = pickle.load(open(f"{MODEL_DIR}/buyability_model.pkl", "rb"))
imputer = pickle.load(open(f"{MODEL_DIR}/feature_imputer.pkl", "rb"))
features = pickle.load(open(f"{MODEL_DIR}/buyability_features.pkl", "rb"))
health_threshold = pickle.load(open(f"{MODEL_DIR}/health_threshold.pkl", "rb"))
feature_weights = pickle.load(open(f"{MODEL_DIR}/feature_weights.pkl", "rb"))

# Numerical features used by the model
num_features = [
    "CCM",
    "Beygir Gucu",
    "Km",
    "Model Yıl",
    "car_age",
    "km_per_year"
]


def parse_ccm(val):
    """Parse CCM (engine volume) from string format"""
    txt = str(val)
    m = re.findall(r"(\d+)-(\d+)", txt)
    if m:
        a, b = map(int, m[0])
        return (a + b) / 2
    m = re.findall(r"(\d+)", txt)
    return int(m[0]) if m else np.nan


def parse_hp(val):
    """Parse horsepower from string format"""
    txt = str(val)
    m = re.findall(r"(\d+)-(\d+)", txt)
    if m:
        a, b = map(int, m[0])
        return (a + b) / 2
    m = re.findall(r"(\d+)", txt)
    return int(m[0]) if m else np.nan


def calculate_health_score(row, weights):
    """
    Calculate composite health score from individual features.
    Returns health score (0-1) and individual component scores.
    """
    # Age score: newer is better (0-20 years range)
    age_score = float(np.clip(1 - (row['car_age'] / 20), 0, 1))

    # km_per_year score: lower usage is better (0-30000 km/year range)
    km_per_year_score = float(np.clip(1 - (row['km_per_year'] / 30000), 0, 1))

    # Total km score: lower mileage is better (0-400000 km range)
    km_score = float(np.clip(1 - (row['Km'] / 400000), 0, 1))

    # Model year score: more recent is better (1959-2025 range)
    year_score = float(np.clip((row['Model Yıl'] - 1959) / (CURRENT_YEAR - 1959), 0, 1))

    # HP score: higher power is better (50-250 HP range)
    hp_score = float(np.clip((row['Beygir Gucu'] - 50) / 200, 0, 1))

    # CCM score: optimal around 1450cc, penalize extremes
    ccm_score = float(np.clip(1 - (abs(row['CCM'] - 1450) / 1000), 0, 1))

    # Composite weighted score
    health_score = (
        weights['age'] * age_score +
        weights['km_per_year'] * km_per_year_score +
        weights['total_km'] * km_score +
        weights['model_year'] * year_score +
        weights['hp'] * hp_score +
        weights['ccm'] * ccm_score
    )

    score_components = {
        'age_score': round(age_score, 3),
        'km_per_year_score': round(km_per_year_score, 3),
        'km_score': round(km_score, 3),
        'year_score': round(year_score, 3),
        'hp_score': round(hp_score, 3),
        'ccm_score': round(ccm_score, 3)
    }

    return health_score, score_components


def get_risk_factors(row, score_components):
    """Identify specific risk factors for the vehicle"""
    risks = []

    # Check for concerning values
    if row['car_age'] > 15:
        risks.append(f"High vehicle age: {int(row['car_age'])} years old")
    elif row['car_age'] > 10:
        risks.append(f"Moderate vehicle age: {int(row['car_age'])} years old")

    if row['km_per_year'] > 20000:
        risks.append(f"High yearly mileage: {int(row['km_per_year']):,} km/year")
    elif row['km_per_year'] > 15000:
        risks.append(f"Above average yearly mileage: {int(row['km_per_year']):,} km/year")

    if row['Km'] > 250000:
        risks.append(f"Very high total mileage: {int(row['Km']):,} km")
    elif row['Km'] > 150000:
        risks.append(f"High total mileage: {int(row['Km']):,} km")

    if row['Beygir Gucu'] < 80:
        risks.append(f"Low engine power: {int(row['Beygir Gucu'])} HP")

    if row['CCM'] < 1200:
        risks.append(f"Small engine size: {int(row['CCM'])} cc")
    elif row['CCM'] > 2000:
        risks.append(f"Large engine size: {int(row['CCM'])} cc (higher maintenance)")

    # Identify weakest scoring component
    weakest = min(score_components.items(), key=lambda x: x[1])
    if weakest[1] < 0.4:
        feature_names = {
            'age_score': 'Vehicle age',
            'km_per_year_score': 'Yearly mileage',
            'km_score': 'Total mileage',
            'year_score': 'Model year',
            'hp_score': 'Engine power',
            'ccm_score': 'Engine size'
        }
        risks.append(f"Weakest factor: {feature_names.get(weakest[0], weakest[0])} (score: {weakest[1]:.2f})")

    return risks


def risk_score_to_text(risk_score):
    """Convert risk score (0-100) to descriptive text"""
    if risk_score >= 86:
        return "Minimal risk - Excellent condition vehicle"
    elif risk_score >= 71:
        return "Very low risk - Good condition vehicle"
    elif risk_score >= 51:
        return "Low risk - Generally acceptable condition"
    elif risk_score >= 31:
        return "Moderate risk - Some concerns, thorough inspection recommended"
    else:
        return "High risk - Multiple concerns with vehicle condition"


def feature_to_description(feature_name):
    """Convert feature name to human-readable description"""
    mapping = {
        "Km": "Total mileage",
        "Model Yıl": "Model year",
        "car_age": "Vehicle age",
        "km_per_year": "Yearly mileage",
        "CCM": "Engine displacement",
        "Beygir Gucu": "Engine power"
    }
    return mapping.get(feature_name, feature_name)


def predict_buyability(sample: dict):
    """
    Predict buyability for a car based on 6 numerical features only.

    Args:
        sample: Dictionary with car features:
            - Model Yıl: Model year (int)
            - Km: Total mileage (int)
            - CCM: Engine volume (string or int)
            - Beygir Gucu: Horsepower (string or int)

    Returns:
        Dictionary with:
            - risk_score: 0-100 (higher = safer to buy)
            - decision: "BUYABLE" or "NOT BUYABLE"
            - probability: Model's raw probability (0-1)
            - health_score: Composite health score (0-1)
            - risk_factors: List of specific concerns
            - feature_scores: Individual feature scores
            - top_features: Top 3 contributing features
            - explanation: Text description of the risk level
    """
    # Parse input into DataFrame
    df = pd.DataFrame([sample])

    # Parse CCM and HP if they're strings
    if 'CCM' in df.columns:
        df['CCM'] = df['CCM'].apply(parse_ccm)
    if 'Beygir Gucu' in df.columns:
        df['Beygir Gucu'] = df['Beygir Gucu'].apply(parse_hp)

    # Create derived features
    df['car_age'] = CURRENT_YEAR - df['Model Yıl']
    df['car_age'] = df['car_age'].clip(lower=1)
    df['km_per_year'] = df['Km'] / df['car_age']

    # Ensure all features exist
    for col in features:
        if col not in df.columns:
            df[col] = np.nan

    # Impute missing values
    df[features] = imputer.transform(df[features])

    # Get model prediction
    X = df[features]
    probability = float(classifier.predict_proba(X)[0][1])

    # Calculate health score
    row = df.iloc[0]
    health_score, score_components = calculate_health_score(row, feature_weights)

    # Convert health score to risk score (0-100)
    # Using health_score instead of probability for more granular results
    risk_score = int(round(health_score * 100))

    # Determine decision based on health score threshold (0.5 = 50/100)
    decision = "BUYABLE" if health_score >= 0.5 else "NOT BUYABLE"

    # Identify risk factors
    risk_factors = get_risk_factors(row, score_components)

    # Get top contributing features
    importances = classifier.feature_importances_
    feature_importance_pairs = sorted(
        zip(features, importances),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    top_features = []
    for feat, imp in feature_importance_pairs:
        top_features.append({
            'feature': feature_to_description(feat),
            'value': float(row[feat]),
            'importance': round(float(imp), 3)
        })

    return {
        'risk_score': risk_score,
        'decision': decision,
        'probability': round(probability, 3),
        'health_score': round(health_score, 3),
        'risk_factors': risk_factors,
        'feature_scores': score_components,
        'top_features': top_features,
        'explanation': risk_score_to_text(risk_score)
    }


# Test the model when running directly
if __name__ == "__main__":
    # Test case 1: Good condition car
    sample_good = {
        "Model Yıl": 2020,
        "Km": 50000,
        "CCM": "1560",
        "Beygir Gucu": "120"
    }

    # Test case 2: Poor condition car
    sample_poor = {
        "Model Yıl": 2005,
        "Km": 320000,
        "CCM": "1390",
        "Beygir Gucu": "75"
    }

    # Test case 3: Average car
    sample_avg = {
        "Model Yıl": 2015,
        "Km": 120000,
        "CCM": "1600",
        "Beygir Gucu": "110"
    }

    print("=" * 60)
    print("BUYABILITY PREDICTION TEST")
    print("=" * 60)

    for name, sample in [("GOOD CONDITION", sample_good),
                         ("POOR CONDITION", sample_poor),
                         ("AVERAGE", sample_avg)]:
        print(f"\n--- {name} CAR ---")
        print(f"Input: Year={sample['Model Yıl']}, Km={sample['Km']}, "
              f"CCM={sample['CCM']}, HP={sample['Beygir Gucu']}")

        result = predict_buyability(sample)

        print(f"\nRisk Score: {result['risk_score']}/100")
        print(f"Decision: {result['decision']}")
        print(f"Probability: {result['probability']}")
        print(f"Health Score: {result['health_score']}")
        print(f"Explanation: {result['explanation']}")

        if result['risk_factors']:
            print("\nRisk Factors:")
            for risk in result['risk_factors']:
                print(f"  - {risk}")

        print("\nFeature Scores:")
        for feat, score in result['feature_scores'].items():
            print(f"  - {feat}: {score}")

        print("\nTop Contributing Features:")
        for feat in result['top_features']:
            print(f"  - {feat['feature']}: {feat['value']:.1f} (importance: {feat['importance']})")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
