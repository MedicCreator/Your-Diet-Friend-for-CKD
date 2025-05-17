import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load your API key securely
load_dotenv()
API_KEY = os.getenv("USDA_API_KEY")

# Search food names from USDA
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

# Extract core nutrients
def extract_nutrients(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {}

    nutrients = response.json().get("foodNutrients", [])

    def get_nutrient(name):
        for nutrient in nutrients:
            if name.lower() in nutrient.get("nutrientName", "").lower():
                return nutrient.get("value")
        return None

    return {
        "Calories": get_nutrient("Energy"),
        "Sodium (mg)": get_nutrient("Sodium"),
        "Potassium (mg)": get_nutrient("Potassium"),
        "Phosphorus (mg)": get_nutrient("Phosphorus")
    }

# Get nutrition data for all searched foods
def get_food_info(query):
    matches = search_foods(query)
    food_info = []
    for food in matches:
        nutrients = extract_nutrients(food["fdcId"])
        if nutrients:
            suggestion = []
            if nutrients["Potassium (mg)"] and nutrients["Potassium (mg)"] > 300:
                suggestion.append("Consider lower-potassium alternatives (e.g., berries, apples).")
            if nutrients["Phosphorus (mg)"] and nutrients["Phosphorus (mg)"] > 150:
                suggestion.append("Limit phosphorus-rich foods (e.g., reduce dairy, beans).")
            if nutrients["Sodium (mg)"] and nutrients["Sodium (mg)"] > 140:
                suggestion.append("Choose low-sodium or fresh versions.")

            food_info.append({
                "Food": food["description"],
                **nutrients,
                "CKD-Friendly Suggestions": "; ".join(suggestion) if suggestion else "OK"
            })
    return pd.DataFrame(food_info)

# Streamlit UI
st.title("Diet Analyzer for Kidney Disease")

user_input = st.text_input("Enter a food name (e.g., salmon, banana, rice):")

if st.button("Analyze"):
    if not user_input:
        st.warning("Please enter a food name.")
    else:
        result_df = get_food_info(user_input)
        if not result_df.empty:
            st.dataframe(result_df)
        else:
            st.error("No results found or API error.")
