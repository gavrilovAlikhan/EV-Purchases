import streamlit as st
import requests

postcodes_json = requests.get("http://127.0.0.1:8000/postcodes").json()


st.set_page_config(page_title="EV bonus check", page_icon=":material/electric_car:")

st.title("EV purchase bonus", icon=":material/electric_car:")
st.caption(
    "Answer a few questions to see if you qualify for the $3,000 government bonus."
)


# with st.form("Submit form"):
#     age = st.number_input("Enter your age", min_value=18)
#     income = st.number_input(
#         "Enter your annual income ($)",
#         min_value=0.0,
#         value=0.0,
#         step=1000.0,
#         format="%.2f",
#     )
#     daily_commute = st.number_input(
#         "Enter your estimated daily commute (km)", min_value=0
#     )
#     cars = st.number_input("How many cars do you currently have?", min_value=0)
#     concern = float(
#         st.segmented_control(
#             "How concerned you are about environment (1 - low, 5 - high)",
#             options=[1, 2, 3, 4, 5],
#             default=1,
#         )
#     )
#     home_charging = st.checkbox(
#         "I can charge EV at home",
#     )
#     range_anxiety = st.segmented_control(
#         "How concerned you are about EV range capacity?",
#         options=["Low", "Medium", "High"],
#     )
#     current_car = st.segmented_control(
#         "What is your current car type?",
#         options=["Sedan", "SUV", "Hatchback", "Truck"],
#     )
#     subsidy = st.checkbox(
#         "I receive government subsidy",
#     )
#     home_postcode = st.selectbox(
#         "What is your home postcode?", options=postcodes_json["Home_Postcodes"]
#     )

#     work_postcode = st.selectbox(
#         "What is your work postcode?", options=postcodes_json["Work_Postcodes"]
#     )

with st.form("ev_form", border=False):
    with st.container(border=True):
        st.subheader("About you", icon=":material/person:")
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=18)
        income = c2.number_input("Annual income ($)", min_value=0.0, step=1000.0)

    with st.container(border=True):
        st.subheader("Driving habits", icon=":material/directions_car:")
        c1, c2 = st.columns(2)
        daily_commute = c1.number_input("Daily commute (km)", min_value=0)
        cars = c2.number_input("Cars owned", min_value=0)
        current_car = st.segmented_control(
            "Current car type", ["Sedan", "SUV", "Hatchback", "Truck"]
        )

    with st.container(border=True):
        st.subheader("Location", icon=":material/location_on:")
        c1, c2 = st.columns(2)
        home_postcode = c1.selectbox(
            "Home postcode", options=postcodes_json["Home_Postcodes"]
        )
        work_postcode = c2.selectbox(
            "Work postcode", options=postcodes_json["Work_Postcodes"]
        )

    with st.container(border=True):
        st.subheader("Your views", icon=":material/eco:")
        concern = st.segmented_control(
            "Environmental concern", [1, 2, 3, 4, 5], default=1
        )
        range_anxiety = st.segmented_control("Range anxiety", ["Low", "Medium", "High"])
        home_charging = st.toggle("I can charge at home")
        subsidy = st.toggle("I already receive a government subsidy")

    submitted = st.form_submit_button(
        "Check eligibility", type="primary", icon=":material/send:", width="stretch"
    )
