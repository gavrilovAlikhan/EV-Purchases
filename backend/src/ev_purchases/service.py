import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, field_serializer
import joblib
from ev_purchases.feature_engineering import engineer_features
from lightgbm import LGBMClassifier
from ev_purchases.data_loader import load_data
from pathlib import Path
from ev_purchases.utils.generate_postcode_lookup import generate_postcode_station_lookup

# File loading
ROOT = Path(__file__).resolve().parents[3]
df = load_data(ROOT / "data/raw/train.csv")

# Postcode lookup variables
rng = np.random.default_rng(seed=42)
home_postcodes = generate_postcode_station_lookup(
    rng=rng, df=df, n=50, station_type="Home"
)
work_postcodes = generate_postcode_station_lookup(
    rng=rng, df=df, n=50, station_type="Work"
)

# Model values
bundle = joblib.load(ROOT / "models/model.joblib")
model: LGBMClassifier = bundle["model"]
features = bundle["features"]
dtypes = bundle["dtypes"]

app = FastAPI()


def home_postcode_lookup(postcode: str):
    """Returns number of stations near home and city type

    Args:
        postcode (str): postcode string

    Returns:
        stations: int - number of stations
        city_type: str - area where person lives
    """
    stations = home_postcodes[postcode]["Stations"]
    city_type = home_postcodes[postcode]["City_Type"]
    return stations, city_type


def work_postcode_lookup(postcode: str):
    stations = work_postcodes[postcode]["Stations"]
    return stations


class ClientData(BaseModel):
    age: int = Field(gt=0, lt=120)
    income: float = Field(gt=0)
    daily_commute: float = Field(gt=0)
    cars: int = Field(gt=0)
    concern: float = Field(gt=0)
    home_charging: bool  # "yes"/"no"
    range_anxiety: str  # "low"/"medium"/"high"
    current_car: str
    subsidy: bool  # "yes"/"no"
    home_postcode: str
    work_postcode: str

    @field_validator("range_anxiety", "current_car")
    @classmethod
    def uppercase(cls, v: str) -> str:
        return v.capitalize()


class EnrichedClientData(ClientData):
    stations_near_home: int
    stations_near_work: int
    city_type: str


def to_frame(d: EnrichedClientData) -> pd.DataFrame:
    raw = pd.DataFrame(
        [
            {
                "Age": d.age,
                "Annual_Income_USD": d.income,
                "Daily_Commute_km": d.daily_commute,
                "Number_of_Cars_Owned": d.cars,
                "Charging_Stations_Near_Home": d.stations_near_home,
                "Charging_Stations_Near_Work": d.stations_near_work,
                "Environmental_Concern_Level": d.concern,
                "City_Type": d.city_type,
                "Current_Car_Type": d.current_car,
                "Home_Charging_Possible": "Yes" if d.home_charging else "No",
                "Subsidy_Available": "Yes" if d.subsidy else "No",
                "Range_Anxiety_Level": d.range_anxiety,
            }
        ]
    )
    X = engineer_features(raw)[features]  # same columns, same order
    return X.astype(dtypes)


@app.get("/postcodes")
def return_dict():
    return {
        "Home_Postcodes": list(home_postcodes),
        "Work_Postcodes": list(work_postcodes),
    }


@app.post("/score")
def score(data: ClientData):
    h_stations, city_type = home_postcode_lookup(data.home_postcode)
    w_stations = work_postcode_lookup(data.work_postcode)
    enriched = EnrichedClientData(
        **data.model_dump(),
        stations_near_home=h_stations,
        city_type=city_type,
        stations_near_work=w_stations,
    )
    prediction = model.predict_proba(to_frame(enriched))[0, 1]
    label = bool(prediction >= 0.5)
    return {"approved": bool(label), "proba": prediction}
