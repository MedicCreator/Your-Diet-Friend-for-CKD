import streamlit as st
import requests
import pandas as pd

# Load your USDA API key securely from Streamlit secrets
API_KEY = st.secrets["USDA_API_KEY"]

# Nutrient ID mapping for USDA database
NUTRIENT_IDS = {
    1008: "Calories",
    1003: "Protein (g)",
    1004: "Total Fat (g)",
    1005: "Carbohydrates (g)",
    1093: "Sodium (mg)",
    1092: "Potassium (mg)",
    1091: "Phosphorus (mg)",
    1051: "Water (g)"
}

# Search for foods by name
def search_foods(query, max_results=5):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": max_results
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("foods", [])
    return []

# Get nutrients for a specific FDC food ID
def extract_nutrients(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {}

    data = response.json()
    nutrients = data.get("foodNutrients", [])
    portion = data.get("servingSize")
    portion_unit = data.get("servingSizeUnit")

    result = {
        "Portion Size": f"{portion} {portion_unit}" if portion and portion_unit else "N/A"
    }

    for nutrient in nutrients:
        nutrient_id = nutrient.get("nutrient", {}).get("id")
        if nutrient_id in NUTRIENT_IDS:
            result[NUTRIENT_IDS[nutrient_id]] = nutrient.get("amount")

    return result

# Compile data for display
def get_food_info(query):
    matches = search_foods(query)
    if not matches:
        return pd.DataFrame([{"Food": query, "Error": "❌ No results found. Check spelling or try another food."}])

    food_info = []
    for food in matches:
        nutrients = extract_nutrients(food["fdcId"])
        if nutrients:
            entry = {"Food": food["description"]}
            entry.update(nutrients)
            food_info.append(entry)
    return pd.DataFrame(food_info)

# Streamlit UI
st.title("💊 Diet Analyzer for Kidney Disease (CKD) + Diabetes")

user_input = st.text_input("Enter a food name (e.g., banana, salmon, rice):")

if st.button("Analyze"):
    if not user_input.strip():
        st.warning("Please enter a food name.")
    else:
        cleaned_input = user_input.strip().lower()
        results = get_food_info(cleaned_input)
        st.dataframe(results)
