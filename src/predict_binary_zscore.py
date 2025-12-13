import pickle
import pandas as pd
import numpy as np
import re

MODEL_DIR = "src/models"
CURRENT_YEAR = 2025  


classifier = pickle.load(open(f"{MODEL_DIR}/binary_zscore_model.pkl", "rb"))
features = pickle.load(open(f"{MODEL_DIR}/binary_zscore_features.pkl", "rb"))

# Numeric vs categorical (train ile aynı)
num_features = [
    "CCM",
    "Beygir Gucu",
    "Km",
    "Model Yıl",
    "car_age",        
    "km_per_year"     
]


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


# SCORE & TEXT

def prob_to_score(prob: float) -> int:
    if prob < 0.30:
        return 0
    elif prob < 0.45:
        return 1
    elif prob < 0.60:
        return 2
    elif prob < 0.75:
        return 3
    else:
        return 4

def prob_to_confidence(prob: float) -> str:
    if prob < 0.50:
        return "NOT BUY"
    elif prob < 0.60:
        return "WEAK BUY"
    elif prob < 0.75:
        return "BUY"
    else:
        return "STRONG BUY"


def score_to_text(score: int) -> str:
    messages = {
        0: "The car is significantly below market value. It may have issues or require major repairs.",
        1: "The car is in the low-price range. It might be a good deal, but should be inspected carefully.",
        2: "The car is in the average price range. It is fairly priced according to the market.",
        3: "The car is in a good price range. Considering its price-performance ratio, it may be worth buying.",
        4: "The car is in an excellent price range! It is below the market average — a potential opportunity."
    }
    return messages.get(score, "Unknown")

def feature_to_reason(feature_name):
    mapping = {
        "Km": "Low mileage",
        "Model Yıl": "Newer model year",
        "car_age": "Old vehicle age",              
        "km_per_year": "High yearly mileage",     
        "CCM": "Engine displacement",
        "Beygir Gucu": "Engine power",
        "Marka": "Brand reputation",
        "Vites": "Transmission type",
        "Yakıt Turu": "Fuel type",
        "Kasa Tipi": "Body type",
        "Kimden": "Seller type",
        "Durum": "Vehicle condition",
        "Arac Tip": "Model popularity"
    }
    return mapping.get(feature_name, feature_name)


# SAFE BUY DECISION 

def safe_buy_decision(prob, car_age, km_per_year, hp):
    """
    Final decision with safety rules
    """

    # Model yeterince emin değilse
    if prob < 0.75:
        return "NOT BUY", "LOW_MODEL_CONFIDENCE"

    # Araç çok eskiyse
    if car_age > 15:
        return "NOT BUY", "TOO_OLD"

    # Yıllık km aşırı yüksekse
    if km_per_year > 20000:
        return "NOT BUY", "HIGH_YEARLY_MILEAGE"

    # Motor çok zayıfsa
    if hp < 90:
        return "NOT BUY", "LOW_ENGINE_POWER"

    return "BUY", "SAFE_BUY"

def explain_prediction(model, features, top_k=3):
    importances = model.feature_importances_
    df_imp = pd.DataFrame({
        "feature": features,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    return df_imp.head(top_k)["feature"].tolist()


# SINGLE PREDICT

def predict_car(sample: dict):

    df = pd.DataFrame([sample])

    # Parse numeric
    df["CCM"] = df["CCM"].apply(parse_ccm)
    df["Beygir Gucu"] = df["Beygir Gucu"].apply(parse_hp)
    df["car_age"] = CURRENT_YEAR - df["Model Yıl"]
    df["car_age"] = df["car_age"].clip(lower=1)
    df["km_per_year"] = df["Km"] / df["car_age"]
    # Ensure all features exist
    for col in features:
        if col not in df.columns:
            df[col] = np.nan

    # Correct dtypes
    for col in features:
        if col in num_features:
            df[col] = df[col].astype(float)
        else:
            df[col] = df[col].astype("category")

    X_cls = df[features]

    prob = float(classifier.predict_proba(X_cls)[0][1])
    score = prob_to_score(prob)
    label = int(prob >= 0.5)
    confidence = prob_to_confidence(prob)
    final_decision, safety_reason = safe_buy_decision(
    prob=prob,
    car_age=df.loc[0, "car_age"],
    km_per_year=df.loc[0, "km_per_year"],
    hp=df.loc[0, "Beygir Gucu"]
)



    top_features = explain_prediction(classifier, features, top_k=3)
    reasons = [feature_to_reason(f) for f in top_features]

    return {
        "probability": round(prob, 3),
        "score": score,
        "decision": final_decision,
        "safety_reason": safety_reason,
        "confidence": confidence,
        "explanation": score_to_text(score),
        "top_reasons": reasons
    }


# BATCH PREDICT

def predict_batch(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

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

    X_cls = df[features]

    probs = classifier.predict_proba(X_cls)[:, 1]
    scores = [prob_to_score(p) for p in probs]

    df["probability"] = probs.round(3)
    df["score"] = scores
    df["decision"] = ["BUY" if p >= 0.5 else "NOT BUY" for p in probs]
    df["explanation"] = [score_to_text(s) for s in scores]

    top_features = explain_prediction(classifier, features, top_k=3)
    top_reasons = [feature_to_reason(f) for f in top_features]
    df["top_reasons"] = [top_reasons] * len(df)

    return df


# TEST

if __name__ == "__main__":

    sample= {
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
