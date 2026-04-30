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


# ✅ Classification function
def classify_pollution(value):
    if value < 5:
        return "Low Pollution"
    elif value < 10:
        return "Moderate Pollution"
    else:
        return "High Pollution"


# ✅ NEW: Detailed analysis generator
def generate_detailed_analysis(input_data, prediction, category):
    analysis = []

    ph = float(input_data.get("ph", 7))
    turbidity = float(input_data.get("turbidity", 0))
    temperature = float(input_data.get("temperature", 25))

    # pH analysis
    if ph < 6.5:
        analysis.append("Water is acidic (pH < 6.5), which may cause pipe corrosion and irritation.")
    elif ph > 8.5:
        analysis.append("Water is alkaline (pH > 8.5), which may indicate contamination or mineral imbalance.")
    else:
        analysis.append("pH level is within the safe drinking range (6.5–8.5).")

    # Turbidity analysis
    if turbidity > 5:
        analysis.append("High turbidity detected (>5 NTU), indicating possible microbial contamination.")
    elif turbidity > 1:
        analysis.append("Moderate turbidity detected. Filtration is recommended before consumption.")
    else:
        analysis.append("Water clarity is good with low turbidity.")

    # Temperature analysis
    if temperature > 30:
        analysis.append("High temperature may promote bacterial growth in water.")
    elif temperature < 10:
        analysis.append("Low temperature — generally safe but may affect taste.")
    else:
        analysis.append("Temperature is within a normal and safe range.")

    # Final summary
    summary = f"Overall water quality is classified as {category}. "

    if "High" in category:
        summary += "Water is not safe for direct consumption and requires treatment."
    elif "Moderate" in category:
        summary += "Water should be treated (boiling/filtration) before use."
    else:
        summary += "Water is generally safe for consumption."

    return summary, analysis


# ✅ Main prediction function
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

    # ✅ NEW: Generate detailed output
    summary, analysis = generate_detailed_analysis(input_data, prediction, category)

    # Return everything
    return prediction, category, summary, analysis