import streamlit as st
import requests
import pandas as pd

API_KEY = st.secrets["USDA_API_KEY"]

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

def extract_nutrients(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {}

    nutrients = response.json().get("foodNutrients", [])

    def get_nutrient(name):
        for nutrient in nutrients:
            if name.lower() == nutrient.get("nutrientName", "").lower():
                return nutrient.get("value")
        return None

    return {
        "Calories": get_nutrient("Energy"),
        "Protein (g)": get_nutrient("Protein"),
        "Total Fat (g)": get_nutrient("Total lipid (fat)"),
        "Carbohydrates (g)": get_nutrient("Carbohydrate, by difference"),
        "Sodium (mg)": get_nutrient("Sodium, Na"),
        "Potassium (mg)": get_nutrient("Potassium, K"),
        "Phosphorus (mg)": get_nutrient("Phosphorus, P"),
        "Water (g)": get_nutrient("Water")
    }

def get_food_info(query):
    matches = search_foods(query)
    if not matches:
        return pd.DataFrame([{"Food": query, "Error": "❌ No results found. Check spelling or try another food."}])

    food_info = []
    for food in matches:
        nutrients = extract_nutrients(food["fdcId"])
        if nutrients:
            food_info.append({
                "Food": food["description"],
                **nutrients
            })
    return pd.DataFrame(food_info)

st.title("💊 Diet Analyzer for Kidney Disease (CKD) + Diabetes")

user_input = st.text_input("Enter a food name (e.g., banana, salmon, rice):")

if st.button("Analyze"):
    if not user_input.strip():
        st.warning("Please enter a food name.")
    else:
        cleaned_input = user_input.strip().lower()
        results = get_food_info(cleaned_input)
        st.dataframe(results)
