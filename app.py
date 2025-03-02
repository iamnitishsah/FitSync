import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.graph_objects as go
from io import StringIO
import base64
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="Health Analyzer", page_icon="🏥", layout="wide")


@st.cache_resource
def load_resources():
    try:
        rfmodel = pickle.load(open('rfmodel.pkl', 'rb'))
        scaler = pickle.load(open('scaler.pkl', 'rb'))
        return rfmodel, scaler
    except:
        st.error("Error loading model or scaler!")
        return None, None


rfmodel, scaler = load_resources()


def get_health_category(score):
    if score >= 8:
        return "Excellent", "Your lifestyle shines as a beacon of health!"
    elif score >= 7:
        return "Very Good", "Great job—small tweaks can take you to the top!"
    elif score >= 6:
        return "Good", "You’ve got a solid base—ready to level up?"
    elif score >= 5:
        return "Fair", "Some habits need love to unlock your best self."
    else:
        return "Needs Improvement", "Time to take charge—small steps, big wins!"


def calculate_bmr(age, weight, height, gender_male):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender_male else -161)


def generate_insights(user_data):
    insights = []
    sleep = round(user_data['Sleep_Hours'][0], 1)
    exercise = round(user_data['Exercise_Hours'][0], 1)
    water = round(user_data['Water_Intake_Liters'][0], 1)
    steps = user_data['Daily_Steps'][0]
    bmi = round(user_data['BMI'][0], 1)
    calories = user_data['Calories_Consumed'][0]
    gender_male = user_data['Gender_Male'][0]
    stress_high = user_data['Stress_Level_High'][0]
    stress_medium = user_data['Stress_Level_Medium'][0]
    age = user_data['Age'][0]
    height = user_data['Height'][0]
    weight = bmi * ((height / 100) ** 2)
    bmr = calculate_bmr(age, weight, height, gender_male)

    insights.append(("Physical Activity", [
        ("red", f"💤 Sleep: {sleep}h < 7h. Try a 10 PM bedtime.") if sleep < 7 else
        ("yellow", f"💤 Sleep: {sleep}h > 9h. Limit screens before bed.") if sleep > 9 else
        ("green", f"💤 Sleep: {sleep}h is perfect!"),
        ("red", f"🏃 Exercise: {exercise}h/day < 0.5h. Start with 15-min walks!") if exercise < 0.5 else
        ("yellow", f"🏃 Exercise: {exercise}h/day—aim for 1h.") if exercise < 1 else
        ("green", f"🏃 Exercise: {exercise}h/day rocks!"),
        ("red", f"👟 Steps: {steps}/day < 5,000. Take the stairs.") if steps < 5000 else
        ("yellow", f"👟 Steps: {steps}/day—push to 10,000!") if steps < 7500 else
        ("green", f"👟 Steps: {steps}/day is active living!")
    ]))

    insights.append(("Nutrition & Hydration", [
        ("red", f"💧 Hydration: {water}L < 2L. Carry a bottle!") if water < 1.99 else
        ("green", f"💧 Hydration: {water}L is spot-on!"),
        ("red", f"⚖️ BMI: {bmi} < 18.5. Boost protein!") if bmi < 18.5 else
        ("green", f"⚖️ BMI: {bmi} is ideal!") if bmi < 25 else
        ("yellow", f"⚖️ BMI: {bmi} (overweight). Cut soda!") if bmi < 30 else
        ("red", f"⚖️ BMI: {bmi} (obese). Less sugar!"),
        ("red", f"🍽️ Nutrition: {calories} kcal < {int(bmr * 0.8)}. Add oats!") if calories < bmr * 0.8 else
        ("yellow", f"🍽️ Nutrition: {calories} kcal > {int(bmr * 1.2)}. Swap chips!") if calories > bmr * 1.2 else
        ("green", f"🍽️ Nutrition: {calories} kcal matches your {int(bmr)} BMR!")
    ]))

    insights.append(("Mental Well-being", [
        ("red", "🧠 Stress: High. Try 5-min breaths.") if stress_high else
        ("yellow", "🧠 Stress: Moderate. Unwind with a hobby.") if stress_medium else
        ("green", "🧠 Stress: Low is golden!")
    ]))

    return insights


def get_user_input():
    st.subheader("Tell Us About You")
    tabs = st.tabs(["Personal", "Activity", "Nutrition"])

    with tabs[0]:
        age = st.number_input("Age", 0, 120, 25)
        gender = st.selectbox("Gender", ["Male", "Female"])
        weight = st.number_input("Weight (kg)", 0.0, 500.0, 70.0)
        height = st.number_input("Height (cm)", 0.0, 300.0, 170.0)
        bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 else 0
        st.write(f"**BMI:** {bmi}")

    with tabs[1]:
        daily_steps = st.number_input("Daily Steps", 0, 100000, 5000)
        exercise_hours = st.number_input("Exercise (h/day)", 0.0, 24.0, 1.0)
        sleep_hours = st.number_input("Sleep (h/night)", 0.0, 24.0, 8.0)

    with tabs[2]:
        water_intake = st.number_input("Water (L/day)", 0.0, 20.0, 2.0)
        calories = st.number_input("Calories/day", 0, 10000, 2000)
        stress = st.selectbox("Stress Level", ["Low", "Medium", "High"])

    user_df = pd.DataFrame({
        'Age': [age], 'Daily_Steps': [daily_steps], 'Calories_Consumed': [calories],
        'Sleep_Hours': [sleep_hours], 'Water_Intake_Liters': [water_intake],
        'Exercise_Hours': [exercise_hours], 'BMI': [bmi], 'Gender_Male': [1 if gender == "Male" else 0],
        'Stress_Level_Medium': [1 if stress == "Medium" else 0], 'Stress_Level_High': [1 if stress == "High" else 0],
        'Height': [height]
    })
    transform_df = user_df.drop(columns=['Height'])
    return scaler.transform(transform_df.values), user_df


def plot_radar_chart(user_data):
    categories = ['Sleep', 'Exercise', 'Steps', 'Hydration', 'BMI', 'Nutrition', 'Stress']
    values = [
        min(user_data['Sleep_Hours'][0] / 9, 1), min(user_data['Exercise_Hours'][0] / 2, 1),
        min(user_data['Daily_Steps'][0] / 10000, 1), min(user_data['Water_Intake_Liters'][0] / 3, 1),
        1 - abs((user_data['BMI'][0] - 21.5) / 21.5) if 18.5 <= user_data['BMI'][0] <= 25 else 0.5,
        min(user_data['Calories_Consumed'][0] / calculate_bmr(user_data['Age'][0], user_data['BMI'][0] * (
                    (user_data['Height'][0] / 100) ** 2), user_data['Height'][0], user_data['Gender_Male'][0]), 1),
        1 if user_data['Stress_Level_High'][0] == 0 and user_data['Stress_Level_Medium'][0] == 0 else 0.5 if
        user_data['Stress_Level_Medium'][0] else 0
    ]
    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False,
                      title="Your Health Profile")
    st.plotly_chart(fig)


def main():
    st.title("Healthy Lifestyle Analyzer")
    st.markdown("Unlock your health potential with personalized insights!")

    with st.expander("How It Works"):
        st.write("Our model scores your lifestyle out of 10 based on global health standards.")

    if rfmodel is None or scaler is None:
        st.error("Model or scaler not loaded. Please check files.")
        return

    user_input, user_df = get_user_input()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyze My Health"):
            with st.spinner("Analyzing..."):
                try:
                    prediction = rfmodel.predict(user_input)[0]
                    category, desc = get_health_category(prediction)

                    if prediction >= 8:
                        st.balloons()

                    st.subheader("Your Health Snapshot")
                    st.progress(prediction / 10)
                    st.metric("Health Score", f"{prediction:.1f}/10", delta=f"{category}")
                    st.write(f"**{desc}**")

                    st.subheader("Insights")
                    insights = generate_insights(user_df)
                    for category, items in insights:
                        with st.expander(category, expanded=True):
                            for color, insight in items:
                                getattr(st,
                                        "success" if color == "green" else "warning" if color == "yellow" else "error")(
                                    insight)

                    plot_radar_chart(user_df)

                    report = StringIO()
                    report.write(f"Health Score: {prediction:.1f}/10 - {category}\n\n")
                    for cat, items in insights:
                        report.write(f"{cat}:\n")
                        for _, insight in items:
                            report.write(f"- {insight}\n")
                    st.download_button("Download Report", data=report.getvalue(), file_name="health_report.txt",
                                       mime="text/plain")

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
    with col2:
        if st.button("Reset"):
            st.session_state.clear()
            st.rerun()

    st.sidebar.header("Daily Health Tip")
    tips = ["Drink water first thing!", "Stretch hourly.", "Swap snacks for fruit."]
    st.sidebar.info(np.random.choice(tips))

    st.markdown("---\nCrafted with ❤️ by [Nitish Sah](https://www.instagram.com/nitishades/)")


if __name__ == "__main__":
    main()