import streamlit as st
import requests

postcodes_json = requests.get("http://127.0.0.1:8000/postcodes").json()

st.title("Are you interested in 3000$ government bonus if you purchase EV")


with st.form("Submit form"):
    age = st.number_input("Enter your age", min_value=18)
    income = st.number_input(
        "Enter your annual income ($)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.2f",
    )
    daily_commute = st.number_input(
        "Enter your estimated daily commute (km)", min_value=0
    )
    cars = st.number_input("How many cars do you currently have?", min_value=0)
    concern = float(
        st.segmented_control(
            "How concerned you are about environment (1 - low, 5 - high)",
            options=[1, 2, 3, 4, 5],
            default=1,
        )
    )
    home_charging = st.checkbox(
        "I can charge EV at home",
    )
    range_anxiety = st.segmented_control(
        "How concerned you are about EV range capacity?",
        options=["Low", "Medium", "High"],
    )
    current_car = st.segmented_control(
        "What is your current car type?",
        options=["Sedan", "SUV", "Hatchback", "Truck"],
    )
    subsidy = st.checkbox(
        "I receive government subsidy",
    )
    home_postcode = st.selectbox(
        "What is your home postcode?", options=postcodes_json["Home_Postcodes"]
    )

    work_postcode = st.selectbox(
        "What is your work postcode?", options=postcodes_json["Work_Postcodes"]
    )
