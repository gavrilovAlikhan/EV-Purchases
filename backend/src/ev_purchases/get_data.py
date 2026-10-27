import zipfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from kaggle.api.kaggle_api_extended import KaggleApi

COMPETITION = "playground-series-s6e9"
RAW_DIR = Path("data/raw")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    api.authenticate()
    api.competition_download_files(COMPETITION, path=RAW_DIR)

    zip_path = RAW_DIR / f"{COMPETITION}.zip"
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(RAW_DIR)
    zip_path.unlink()  # remove the zip once extracted

    print(f"Data saved to {RAW_DIR}")


if __name__ == "__main__":
    main()