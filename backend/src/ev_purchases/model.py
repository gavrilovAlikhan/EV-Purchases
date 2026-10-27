import joblib
import pandas as pd

bundle = joblib.load("./models/model.joblib")
model = bundle["model"]
features = bundle["features"]
dtypes = bundle["dtypes"]

# print(features)
# print(dtypes)
print(model)

# # Prepare new data the same way: correct order, correct types