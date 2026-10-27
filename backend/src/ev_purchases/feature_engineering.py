import pandas as pd
import numpy as np


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    eng_df = df.copy()
    for c in ["Home_Charging_Possible", "Subsidy_Available"]:
        eng_df[c] = eng_df[c].str.lower().map({"no": 0, "yes": 1})

    eng_df["Range_Anxiety_Level"] = (
        eng_df["Range_Anxiety_Level"]
        .str.lower()
        .map({"low": 0, "medium": 1, "high": 2})
    )

    eng_df["Total_Charging_Stations"] = (
        eng_df["Charging_Stations_Near_Home"]
        + eng_df["Charging_Stations_Near_Work"]
        + eng_df["Home_Charging_Possible"]
    )

    eng_df["Realistic_Concern"] = (
        eng_df["Environmental_Concern_Level"] - eng_df["Range_Anxiety_Level"]
    )

    eng_df["Anxiety_Environmental"] = (
        eng_df["Range_Anxiety_Level"].astype(str)
        + "_"
        + eng_df["Environmental_Concern_Level"].astype(str)
    )

    eng_df["Anxiety_Commute_Ratio"] = np.where(
        eng_df["Daily_Commute_km"] == 0,
        0,
        eng_df["Range_Anxiety_Level"] / eng_df["Daily_Commute_km"],
    )

    eng_df["High_Income_EV_Potential"] = (
        eng_df["Annual_Income_USD"] >= 170537.0
    ).astype("int8")
    eng_df["income_per_car"] = eng_df["Annual_Income_USD"] / (
        eng_df["Number_of_Cars_Owned"] + 1
    )

    # Subsidy combinations

    eng_df["subsidy_income"] = eng_df["Annual_Income_USD"] * eng_df["Subsidy_Available"]
    eng_df["subsidy_concern"] = (
        eng_df["Environmental_Concern_Level"] * eng_df["Subsidy_Available"]
    )
    eng_df["home_charging_subsidy"] = (
        eng_df["Home_Charging_Possible"] * eng_df["Subsidy_Available"]
    )

    return eng_df
