import joblib
import pandas as pd
import json

# ✅ Load model
model = joblib.load("models/pollution_model.pkl")

# ✅ Load feature names
with open("models/features.json", "r") as f:
    feature_names = json.load(f)

# ✅ Load feature means
with open("models/feature_means.json", "r") as f:
    feature_means = json.load(f)


# ✅ NEW: Classification function
def classify_pollution(value):
    if value < 5:
        return "Low Pollution"
    elif value < 10:
        return "Moderate Pollution"
    else:
        return "High Pollution"


def predict_pollution(input_data):

    # Create empty DataFrame with correct columns
    sample = pd.DataFrame(columns=feature_names)

    # Fill values correctly
    for feature in feature_names:
        if feature in input_data:
            try:
                sample.at[0, feature] = float(input_data[feature])
            except:
                sample.at[0, feature] = feature_means.get(feature, 0)
        else:
            sample.at[0, feature] = feature_means.get(feature, 0)

    # Ensure all values are numeric
    sample = sample.astype(float)

    # Predict
    prediction = float(model.predict(sample)[0])

    # Classify
    category = classify_pollution(prediction)

    # Return BOTH
    return prediction, category