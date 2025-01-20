import streamlit as st
import pandas as pd
import pickle


rfmodel = pickle.load(open('rfmodel.pkl', 'rb'))

scaler = pickle.load(open('scaler.pkl', 'rb'))

def get_user_input():
    age = st.number_input("Enter your age:", min_value=0, max_value=100, value=25)
    gender = st.selectbox("Enter your gender:", options=["Male", "Female"])
    daily_steps = st.number_input("Enter your daily steps:", min_value=0, value=5000)
    calories_consumed = st.number_input("Enter calories consumed:", min_value=0, value=2000)
    sleep_hours = st.number_input("Enter your average sleep hours:", min_value=0.0, max_value=24.0, value=8.0)
    water_intake_liters = st.number_input("Enter water intake (liters):", min_value=0.0, value=2.0)
    stress_level = st.selectbox("Enter your stress level:", options=["Low", "Medium", "High"])
    exercise_hours = st.number_input("Enter your exercise hours:", min_value=0.0, max_value=24.0, value=1.0)
    bmi = st.number_input("Enter your BMI:", min_value=0.0, value=22.0)

    gender_male = 1 if gender == 'Male' else 0
    stress_level_medium = 1 if stress_level == 'Medium' else 0
    stress_level_high = 1 if stress_level == 'High' else 0

    user_df = pd.DataFrame({
        'Age': [age],
        'Daily_Steps': [daily_steps],
        'Calories_Consumed': [calories_consumed],
        'Sleep_Hours': [sleep_hours],
        'Water_Intake_Liters': [water_intake_liters],
        'Exercise_Hours': [exercise_hours],
        'BMI': [bmi],
        'Gender_Male': [gender_male],
        'Stress_Level_Medium': [stress_level_medium],
        'Stress_Level_High': [stress_level_high]
    })

    user_input = scaler.transform(user_df.values)
    return user_input

def predict(user_input, model):
    prediction = model.predict(user_input)
    return prediction[0]

st.title("Healthy Lifestyle Predictor")

user_input = get_user_input()
if st.button("Predict"):
    prediction = predict(user_input, rfmodel)
    st.write(f'Predicted Healthy Lifestyle Score: {prediction:.2f}')


st.markdown(
    """
    ---
    Made with ❤️ by [Nitish Sah](https://www.instagram.com/nitishadow/) just for you.
    """
)