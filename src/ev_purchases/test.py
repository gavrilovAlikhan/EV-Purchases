from ev_purchases.utils.generate_postcode_lookup import generate_postcode_station_lookup
from ev_purchases.data_loader import load_data
from pathlib import Path



ROOT = Path(__file__).resolve().parents[2]
df = load_data(ROOT / "data/raw/train.csv")