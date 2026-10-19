import streamlit as st
import requests

postcodes_json = requests.get("http://127.0.0.1:8000/postcodes").json()


st.set_page_config(page_title="EV bonus check", page_icon=":material/electric_car:")

st.title("EV purchase bonus", icon=":material/electric_car:")
st.caption(
    "Answer a few questions to see if you qualify for the $3,000 government bonus."
)


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

if submitted:
    data = {
        "age": age,
        "income": income,
        "daily_commute": daily_commute,
        "cars": cars,
        "concern": concern,
        "home_charging": home_charging,
        "range_anxiety": range_anxiety,
        "current_car": current_car,
        "subsidy": subsidy,
        "home_postcode": home_postcode,
        "work_postcode": work_postcode,
    }

    response = requests.post("http://127.0.0.1:8000/score", json=data)
    proba = response.json()['proba']
    if response.json()['approved']:
        st.success("Thank you for your interest, we will review you form", icon=":material/check_circle:")
        st.info(f"The customer likely will make a purchase. Model purchase probability: {proba:.3f}")
    else:
        st.success("Thank you for your interest, we will review you form", icon=":material/check_circle:")
        st.info(f"The customer likely will not make a purchase. Model purchase probability: {proba:.3f}")


