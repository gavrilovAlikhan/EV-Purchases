from ev_purchases.utils.generate_postcode_lookup import generate_postcode_station_lookup
from ev_purchases.data_loader import load_data
from pathlib import Path
import requests



# ROOT = Path(__file__).resolve().parents[2]
# df = load_data(ROOT / "data/raw/train.csv")

dict_1 = requests.get("http://127.0.0.1:8000/postcodes").json()

print(dict_1['Home_Postcodes'])
