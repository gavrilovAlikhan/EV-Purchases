import numpy as np
import pandas as pd
from pathlib import Path
from ev_purchases.data_loader import load_data
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

# print(home_postcodes)
# print(list(home_postcodes))

test_dict = {
    "Home_Postcodes": [
        f"{k} (City Type: {v['City_Type']}, ⚡Stations: {v['Stations']})"
        for k, v in home_postcodes.items()
    ],
    "Work_Postcodes": [
        f"{k} (⚡Stations: {v['Stations']})"
        for k, v in work_postcodes.items()
    ],
}


test_list = [
        f"{k} (City Type: {v['City_Type']}, ⚡Stations: {v['Stations']})"
        for k, v in home_postcodes.items()
    ]

a = test_list[0]

print(a)
print(a.split(" ("))
