import pickle
import pandas as pd
import numpy as np
import re


MODEL_DIR = "src/models"
CURRENT_YEAR = 2025

BUY_THRESHOLD = 0.70
CONDITIONAL_THRESHOLD = 0.55


classifier = pickle.load(open(f"{MODEL_DIR}/binary_zscore_model.pkl", "rb"))
features = pickle.load(open(f"{MODEL_DIR}/binary_zscore_features.pkl", "rb"))
imputer = pickle.load(open(f"{MODEL_DIR}/imputer.pkl", "rb"))


num_features = [
    "CCM",
    "Beygir Gucu",
    "Km",
    "Model Yıl",
    "car_age",
    "km_per_year"
]


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



def compute_penalty(car_age, km_per_year, hp):
    penalty = 0.0
    reasons = []

    if car_age > 15:
        penalty += 0.10
        reasons.append("OLD_VEHICLE")

    if km_per_year > 20000:
        penalty += 0.08
        reasons.append("HIGH_YEARLY_MILEAGE")

    if hp < 90:
        penalty += 0.07
        reasons.append("LOW_ENGINE_POWER")

    return penalty, reasons



def decision_engine(final_score):
    if final_score >= BUY_THRESHOLD:
        return "BUY"
    elif final_score >= CONDITIONAL_THRESHOLD:
        return "CONDITIONAL BUY"
    else:
        return "NOT BUY"

def explain_prediction(model, features, top_k=3):
    importances = model.feature_importances_
    df_imp = pd.DataFrame({
        "feature": features,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    return df_imp.head(top_k)["feature"].tolist()

def feature_to_reason(feature_name):
    mapping = {
        "Km": "Mileage",
        "Model Yıl": "Model year",
        "car_age": "Vehicle age",
        "km_per_year": "Yearly mileage",
        "CCM": "Engine displacement",
        "Beygir Gucu": "Engine power",
        "Marka": "Brand",
        "Vites": "Transmission",
        "Yakıt Turu": "Fuel type",
        "Kasa Tipi": "Body type",
        "Kimden": "Seller type",
        "Durum": "Vehicle condition",
        "Arac Tip": "Model popularity"
    }
    return mapping.get(feature_name, feature_name)



def predict_car(sample: dict):

    df = pd.DataFrame([sample])
    
    df["CCM"] = df["CCM"].apply(parse_ccm)
    df["Beygir Gucu"] = df["Beygir Gucu"].apply(parse_hp)

    df["car_age"] = CURRENT_YEAR - df["Model Yıl"]
    df["car_age"] = df["car_age"].clip(lower=1)
    df["km_per_year"] = df["Km"] / df["car_age"]

    for col in features:
        if col not in df.columns:
            df[col] = np.nan

    for col in features:
        if col in num_features:
            df[col] = df[col].astype(float)
        else:
            df[col] = df[col].astype("category")

    df[num_features] = imputer.transform(df[num_features])

    X = df[features]

    prob = float(classifier.predict_proba(X)[0][1])

    penalty, risk_reasons = compute_penalty(
        car_age=df.loc[0, "car_age"],
        km_per_year=df.loc[0, "km_per_year"],
        hp=df.loc[0, "Beygir Gucu"]
    )

    final_score = prob - penalty
    decision = decision_engine(final_score)

    top_features = explain_prediction(classifier, features)
    reasons = [feature_to_reason(f) for f in top_features]

    return {
        "probability": round(prob, 3),
        "risk_penalty": round(penalty, 2),
        "final_score": round(final_score, 3),
        "decision": decision,
        "risk_reasons": risk_reasons,
        "top_reasons": reasons
    }

if __name__ == "__main__":

    sample = {
        "Model Yıl": 2005,
        "Km": 320000,
        "CCM": "1390",
        "Beygir Gucu": "75",
        "Marka": "Toyota",
        "Yakıt Turu": "Benzin",
        "Vites": "Manuel",
        "Kasa Tipi": "Sedan",
        "Kimden": "Galeriden",
        "Durum": "2. El",
        "Arac Tip": "Corolla"
    }

    print(predict_car(sample))
