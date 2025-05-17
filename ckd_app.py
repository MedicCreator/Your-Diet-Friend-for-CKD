import streamlit as st
import requests
import pandas as pd

# ✅ Load API key securely from Streamlit Secrets
API_KEY = st.secrets["USDA_API_KEY"]

# 🔍 Search food in USDA database
def search_foods(query, max_results=5):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": max_results
    }
    response = requests.get(url, params=params)

    # 🔍 Show debug info directly in the app
    st.write("🔎 API Status:", response.status_code)
    st.write("🔗 Full URL:", response.url)

    try:
        json_data = response.json()
        st.write("📦 Response:", json_data)
    except Exception as e:
        st.error(f"❌ Failed to parse JSON: {e}")
        return []

    if response.status_code == 200:
        return json_data.get("foods", [])
    return []


# 🧪 Extract nutrients from food record
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
        "Protein (g)": get_nutrient("Protein"),
        "Sodium (mg)": get_nutrient("Sodium"),
        "Potassium (mg)": get_nutrient("Potassium"),
        "Phosphorus (mg)": get_nutrient("Phosphorus")
    }

# 📊 Fetch info and provide CKD recommendations
def get_food_info(query):
    matches = search_foods(query)
    if not matches:
        return pd.DataFrame([{"Food": query, "Error": "❌ No results found. Check spelling or try another food."}])

    food_info = []
    for food in matches:
        nutrients = extract_nutrients(food["fdcId"])
        if nutrients:
            suggestions = []
            if nutrients["Potassium (mg)"] and nutrients["Potassium (mg)"] > 300:
                suggestions.append("⚠ High Potassium: Try berries or apples instead.")
            if nutrients["Phosphorus (mg)"] and nutrients["Phosphorus (mg)"] > 150:
                suggestions.append("⚠ High Phosphorus: Limit dairy, beans.")
            if nutrients["Sodium (mg)"] and nutrients["Sodium (mg)"] > 140:
                suggestions.append("⚠ High Sodium: Choose fresh or low-sodium options.")
            if nutrients["Protein (g)"] and nutrients["Protein (g)"] > 20:
                suggestions.append("⚠ High Protein: Monitor intake with your doctor.")

            food_info.append({
                "Food": food["description"],
                **nutrients,
                "CKD Suggestions": "; ".join(suggestions) if suggestions else "✅ OK"
            })
    return pd.DataFrame(food_info)

# 🌐 Streamlit UI
st.title("💊 Diet Analyzer for Kidney Disease (CKD)")

user_input = st.text_input("Enter a food name (e.g., banana, salmon, rice):")

if st.button("Analyze"):
    if not user_input.strip():
        st.warning("Please enter a food name.")
    else:
        cleaned_input = user_input.strip().lower()
        results = get_food_info(cleaned_input)
        st.dataframe(results)

