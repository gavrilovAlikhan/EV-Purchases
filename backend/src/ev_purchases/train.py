import numpy as np
import pandas as pd
import lightgbm as lgb
import yaml
from pathlib import Path
from ev_purchases.feature_engineering import engineer_features
from ev_purchases.data_loader import load_data
import joblib

ROOT = Path(__file__).resolve().parents[3]  # set root path to project folder
train_path = f"{ROOT}/data/raw/train.csv"
model_path = f"{ROOT}/models/"

# Load configs
with open(f"{ROOT}/configs/train.yaml", "r") as f:
    config = yaml.safe_load(f)
hyperparameters = config["parameters"]
TARGET = config['data']["target"]
cat_columns = config['data']["categorical_features"]
non_relevant_columns = config['data']["non_relevant_columns"]


# Split training dataset into X and y for model training
def data_splitter(
    df: pd.DataFrame, additional_drop_columns: list = []
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    return: X_train, y_train

    """
    train_dataset = df.drop(columns=non_relevant_columns + additional_drop_columns)

    X_train = train_dataset.drop(columns=[TARGET])
    y_train = train_dataset[TARGET].map({"Yes": 1, "No": 0})

    return X_train, y_train


def train():
    # try training dataset
    try:
        df = load_data(train_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"'{train_path}' is not found, run 'get_data.py' first to download the training data"
        ) from e

    df = engineer_features(df)
    X, y = data_splitter(df)
    model = lgb.LGBMClassifier(**hyperparameters)

    print(f"Training LGBMClassifier with {hyperparameters.get('n_estimators', 'Unknown')} trees on a dataset with {len(X)} samples and {len(X.columns)} features...")
    print(f"\nPrinting logloss every 300 iterations...")
    
    model.fit(
        X,
        y,
        categorical_feature=cat_columns,
        eval_X=X,
        eval_y=y,
        callbacks=[lgb.log_evaluation(period=300)],
    )

    print(f"\nTraining completed. Saving model...")
    bundle = {
        "model": model,  # trained model
        "features": list(X.columns),  # order
        "dtypes": X.dtypes.astype(str).to_dict(),  # type of each feature
    }

    joblib.dump(bundle, f"{model_path}model_test.joblib")
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train()