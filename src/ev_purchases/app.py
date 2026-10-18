import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
import joblib
from ev_purchases.feature_engineering import engineer_features
from lightgbm import LGBMClassifier

class ClientData(BaseModel):
    age: int = Field(gt=0, lt=120)
    income: float = Field(gt=0)
    daily_commute: float = Field(gt=0)
    cars: int = Field(gt=0)
    concern: float = Field(gt=0)
    home_charging: str       # "yes"/"no"
    range_anxiety: str       # "low"/"medium"/"high"
    current_car: str
    subsidy: str             # "yes"/"no"
    stations_near_home: int = Field(gt=0)
    stations_near_work: int = Field(gt=0)
    city_type: str

app = FastAPI()
bundle = joblib.load("./models/model.joblib")
model: LGBMClassifier = bundle["model"]
features = bundle["features"]
dtypes = bundle["dtypes"]

def to_frame(d: ClientData) -> pd.DataFrame:
    raw = pd.DataFrame([{
        "Age": d.age,
        "Annual_Income_USD": d.income,
        "Daily_Commute_km": d.daily_commute,
        "Number_of_Cars_Owned": d.cars,
        "Charging_Stations_Near_Home": d.stations_near_home,
        "Charging_Stations_Near_Work": d.stations_near_work,
        "Environmental_Concern_Level": d.concern,
        "City_Type": d.city_type,
        "Current_Car_Type": d.current_car,
        "Home_Charging_Possible": d.home_charging,
        "Subsidy_Available": d.subsidy,
        "Range_Anxiety_Level": d.range_anxiety,
    }])
    X = engineer_features(raw)[features]          # same columns, same order
    return X.astype(dtypes)  


@app.post("/score")
def score(data: ClientData):
    prediction = model.predict_proba(to_frame(data))[0,1]
    label = bool(prediction >= 0.5)
    return {"approved": bool(label)}


