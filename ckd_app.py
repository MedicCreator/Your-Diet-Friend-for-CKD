import pandas as pd
import streamlit as st

food_data = [
    {"Food": "Boiled Egg", "Calories": 68, "Sodium_mg": 71, "Potassium_mg": 63, "Phosphorus_mg": 95},
    {"Food": "Apple (1 medium)", "Calories": 95, "Sodium_mg": 2, "Potassium_mg": 195, "Phosphorus_mg": 20},
{"Food": "White Bread (1 slice)", "Calories": 66, "Sodium_mg": 134, "Potassium_mg": 37, "Phosphorus_mg": 25},
    {"Food": "Banana (1 medium)", "Calories": 105, "Sodium_mg": 1, "Potassium_mg": 422, "Phosphorus_mg": 22},
    {"Food": "Grilled Chicken (3 oz)", "Calories": 128, "Sodium_mg": 60, "Potassium_mg": 220, "Phosphorus_mg": 196},
    {"Food": "Brown Rice (1 cup)", "Calories": 216, "Sodium_mg": 10, "Potassium_mg": 84, "Phosphorus_mg": 162},
    {"Food": "Broccoli (1/2 cup steamed)", "Calories": 27, "Sodium_mg": 25, "Potassium_mg": 229, "Phosphorus_mg": 32},
    {"Food": "Milk (1 cup)", "Calories": 103, "Sodium_mg": 107, "Potassium_mg": 366, "Phosphorus_mg": 247},
    {"Food": "Oatmeal (1/2 cup cooked)", "Calories": 83, "Sodium_mg": 2, "Potassium_mg": 61, "Phosphorus_mg": 77}
]

food_df = pd.DataFrame(food_data)

def analyze_food_intake(food_items):
    results = []
    for item in food_items:
        match = food_df[food_df["Food"].str.lower().str.contains(item.lower(), na=False)]
        if match.empty:
            results.append({"Food": item, "Error": "Food not found in database."})
            continue

        row = match.iloc[0]
        suggestions = []

        if row["Potassium_mg"] > 300:
            suggestions.append("Consider lower-potassium alternatives (e.g., berries, apples).")
        if row["Phosphorus_mg"] > 150:
            suggestions.append("Limit phosphorus-rich foods (e.g., reduce dairy, beans).")
        if row["Sodium_mg"] > 140:
            suggestions.append("Choose low-sodium or fresh versions.")

        results.append({
            "Food": row["Food"],
            "Calories": row["Calories"],
            "Sodium (mg)": row["Sodium_mg"],
            "Potassium (mg)": row["Potassium_mg"],
            "Phosphorus (mg)": row["Phosphorus_mg"],
            "CKD-Friendly Suggestions": "; ".join(suggestions) if suggestions else "OK"
        })

    return pd.DataFrame(results)

st.title("Diet Analyzer for Kidney Disease")

user_input = st.text_area("Enter food items (comma-separated):", "Banana, Grilled Chicken, Milk")

if st.button("Analyze"):
    food_list = [item.strip() for item in user_input.split(",") if item.strip()]
    if food_list:
        results = analyze_food_intake(food_list)
        st.dataframe(results)
    else:
        st.warning("Please enter at least one food item.")
