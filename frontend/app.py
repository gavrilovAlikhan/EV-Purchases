import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


# @st.cache_data # uncomment to cache the postcodes lookup, but cache should be cleared if postcodes are updated
def get_postcodes() -> dict:
    return requests.get(f"{API_URL}/postcodes").json()


postcodes_json = get_postcodes()
sigmoid = lambda z: 1 / (1 + np.exp(-z)) # needed for shap


def draw_waterfall(res: dict): # feature importance chart

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

st.set_page_config(
    page_title="EV bonus check", page_icon=":material/electric_car:", layout="wide"
)

st.title("EV purchase bonus", icon=":material/electric_car:")
st.caption(
    "Answer a few questions to see if you qualify for the $3,000 government bonus."
)


# Plain container instead of st.form: a form only reruns on submit, so the
# button could not be enabled/disabled live as fields are filled in.
with st.container():
    # 2x2 grid of sections so the whole form fits on one screen.
    # height="stretch" keeps the two cards in each row the same height.
    row1 = st.columns(2)
    row2 = st.columns(2)

    with row1[0].container(border=True, height="stretch"):
        st.subheader("About you", icon=":material/person:")
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=18, max_value=120, value=None, placeholder="18")
        income = c2.number_input(
            "Annual income ($)",
            min_value=0.0,
            value=None,
            step=1000.0,
            placeholder="e.g. 39000",
        )

    with row1[1].container(border=True, height="stretch"):
        st.subheader("Driving habits", icon=":material/directions_car:")
        c1, c2, c3 = st.columns([1, 1, 2])
        daily_commute = c1.number_input("Daily commute (km)", min_value=0, value=None)
        cars = c2.number_input("Cars owned", min_value=0, value=None)
        current_car = c3.segmented_control(
            "Current car type", ["Sedan", "SUV", "Hatchback", "Truck"]
        )

    with row2[0].container(border=True, height="stretch"):
        st.subheader("Location", icon=":material/location_on:")
        c1, c2 = st.columns(2)
        home_postcode = c1.selectbox(
            "Home postcode",
            options=postcodes_json["Home_Postcodes"],
            index=None,
            placeholder="Select postcode",
        )
        work_postcode = c2.selectbox(
            "Work postcode",
            options=postcodes_json["Work_Postcodes"],
            index=None,
            placeholder="Select postcode",
        )

    with row2[1].container(border=True, height="stretch"):
        st.subheader("Your views", icon=":material/eco:")
        c1, c2 = st.columns(2)
        concern = c1.segmented_control(
            "Environmental concern", [1, 2, 3, 4, 5], default=1
        )
        range_anxiety = c2.segmented_control(
            "Range anxiety", ["Low", "Medium", "High"]
        )
        c1, c2 = st.columns(2)
        home_charging = c1.toggle("I can charge at home")
        subsidy = c2.toggle("I already receive a government subsidy")

    # Range limits are enforced by the widgets themselves, so a field is
    # valid as soon as it has a value (None means empty / deselected).
    required = {
        "Age": age,
        "Annual income": income,
        "Daily commute": daily_commute,
        "Cars owned": cars,
        "Current car type": current_car,
        "Home postcode": home_postcode,
        "Work postcode": work_postcode,
        "Environmental concern": concern,
        "Range anxiety": range_anxiety,
    }
    missing = [name for name, value in required.items() if value is None]

    submitted = st.button(
        "Check eligibility",
        type="primary",
        icon=":material/send:",
        width="stretch",
        disabled=bool(missing),
    )
    if missing:
        st.caption(f"Still to fill in: {', '.join(missing)}")

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
        # strip the suffix since API looks postcodes up by the bare code.
        "home_postcode": home_postcode.split(" (")[0],
        "work_postcode": work_postcode.split(" (")[0],
    }

    response = requests.post(f"{API_URL}/score", json=data)
    if not response.ok:
        st.error(f"Scoring failed ({response.status_code})", icon=":material/error:")
        # st.json would try to parse a plain-text body (e.g. "Internal Server
        # Error") as JSON and fail, so only use it for real JSON responses.
        if response.headers.get("content-type", "").startswith("application/json"):
            st.json(response.json())
        else:
            st.code(response.text, language=None)
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
