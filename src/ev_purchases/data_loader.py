import pandas as pd
from pathlib import Path

train_path = Path("data/raw/test.csv")

def load_data(file_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{file_path} is not found") from e
    
    return df


