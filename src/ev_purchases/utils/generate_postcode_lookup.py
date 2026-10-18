import numpy as np
import pandas as pd
from typing import Literal

rng = np.random.default_rng(seed=42)


def generate_station_probability(
    df: pd.DataFrame, station_type: Literal["Home", "Work"]
) -> dict:

    if station_type not in ["Home", "Work"]:
        raise ValueError(
            f"station_type only accepts 'Home' or 'Work' got {station_type!r} instead"
        )

    city_stations_probabilities = {}

    for city in ["Rural", "Urban", "Suburban"]:
        station_distribution = (
            pd.crosstab(
                df["City_Type"],
                df[f"Charging_Stations_Near_{station_type}"],
                normalize="index",
            )
            .loc[f"{city}"]
            .to_dict()
        )

        city_stations_probabilities[f"{city}"] = station_distribution
    return city_stations_probabilities


def random_postcode(rng):
    alphabet = list("ABCDEFGHJKLMNPRSTUWXYZ")
    return (
        str(rng.integers(1, 9))
        + rng.choice(alphabet)
        + rng.choice(alphabet)
        + " "
        + str(rng.integers(1, 9))
        + rng.choice(alphabet)
        + rng.choice(alphabet)
    )


def generate_postcode_station_lookup(
    rng, df: pd.DataFrame, n: int, station_type: Literal["Home", "Work"]
) -> dict:

    if station_type not in ["Home", "Work"]:
        raise ValueError(
            f"station_type only accepts 'Home' or 'Work' got {station_type!r} instead"
        )

    postcodes_dict = {}
    postcodes = set()
    city_stations_probabilities = generate_station_probability(df, station_type)

    while len(postcodes) < n:
        postcodes.add(random_postcode(rng))

    for p in sorted(
        postcodes
    ):  # it makes loop deterministic due to python set hashing tricks
        city_choice = rng.choice(["Rural", "Urban", "Suburban"])
        home_stations = rng.choice(
            a=list(city_stations_probabilities[city_choice].keys()),
            p=list(city_stations_probabilities[city_choice].values()),
        )
        postcodes_dict[p] = {
            "City_Type": str(city_choice),
            "Stations": int(home_stations),
        }

    return postcodes_dict
