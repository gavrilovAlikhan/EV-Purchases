import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
postcodes_json = requests.get(f"{API_URL}/postcodes").json()
sigmoid = lambda z: 1 / (1 + np.exp(-z))


def draw_waterfall(res: dict):

    # --- Sort by absolute impact, top 10 + rest ---
    items = sorted(
        zip(res["feature_names"], res["shap_values"], res["feature_values"]),
        key=lambda t: abs(t[1]),
        reverse=True,
    )

    top, rest = items[:10], items[10:]
    labels = [f"{n} = {v}" for n, _, v in top]
    values = [s for _, s, _ in top]
    if rest:
        labels.append(f"{len(rest)} other features")
        values.append(sum(s for _, s, _ in rest))

    base = res["base_value"]
    final = base + sum(values)

    # --- Data labels: % for ends, log-odds for features ---
    text = (
        [f"{sigmoid(base):.1%}"]
        + [f"{v:+.2f}" for v in values]
        + [f"{sigmoid(final):.1%}"]
    )

    # --- Chart ---
    fig = go.Figure(go.Waterfall(
        orientation="h",
        y=["Average customer"] + labels + ["This customer"],
        x=[base] + values + [0],
        measure=["absolute"] + ["relative"] * len(values) + ["total"],
        text=text,
        textposition=["inside"] + ["outside"] * len(values) + ["inside"],
        insidetextanchor="middle",
        insidetextfont=dict(color="white"),
        cliponaxis=False,
        # increasing={"marker": {"color": "#d62728"}},
        # decreasing={"marker": {"color": "#1f77b4"}},
        # totals={"marker": {"color": "grey"}},
        connector={"line": {"color": "rgba(128,128,128,0.4)"}},
    ))

    # Pad x-axis so outside labels have room
    running = np.cumsum([base] + values)
    lo, hi = min(running.min(), 0), max(running.max(), 0)
    pad = (hi - lo) * 0.12
    fig.update_xaxes(range=[lo - pad, hi + pad])

    fig.update_yaxes(autorange="reversed", tickmode="linear")
    fig.update_layout(
        height=max(600, 28 * (len(labels) + 2)),
        margin=dict(l=220, r=80),
        yaxis_title=None,
        xaxis_title="SHAP value (log-odds)",
        showlegend=False,
        title=dict(
            text="Top 10 prediction contributors",
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(page_title="EV bonus check", page_icon=":material/electric_car:")

st.title("EV purchase bonus", icon=":material/electric_car:")
st.caption(
    "Answer a few questions to see if you qualify for the $3,000 government bonus."
)


with st.form("ev_form", border=False):
    with st.container(border=True):
        st.subheader("About you", icon=":material/person:")
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=18, value=None, placeholder="18")
        income = c2.number_input(
            "Annual income ($)",
            min_value=0.0,
            value=None,
            step=1000.0,
            placeholder="e.g. 39000",
        )

    with st.container(border=True):
        st.subheader("Driving habits", icon=":material/directions_car:")
        c1, c2 = st.columns(2)
        daily_commute = c1.number_input("Daily commute (km)", min_value=0, value=None)
        cars = c2.number_input("Cars owned", min_value=0, value=None)
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

    response = requests.post(f"{API_URL}/score", json=data)
    if not response.ok:
        st.error(f"Scoring failed ({response.status_code})", icon=":material/error:")
        st.json(
            response.json()
            if response.headers.get("content-type") == "application/json"
            else response.text
        )
        st.stop()

    sv = requests.post(f"{API_URL}/explain", json=data)
    result = response.json()
    proba = result["proba"]
    if result["approved"]:
        st.success(
            "Thank you for your interest, we will review you form",
            icon=":material/check_circle:",
        )
        st.info(
            f"The customer likely will make a purchase. Model purchase probability: {proba:.3f}"
        )
    else:
        st.success(
            "Thank you for your interest, we will review you form",
            icon=":material/check_circle:",
        )
        st.info(
            f"The customer likely will not make a purchase. Model purchase probability: {proba:.3f}"
        )


    draw_waterfall(sv.json())
# TODO: remove default values from the form fields and replace with "placeholder" argument

# TODO: add validation of the form to not allow empty fields
