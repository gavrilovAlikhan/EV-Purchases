import joblib


bundle = joblib.load("./models/model.joblib")
model, features, dtypes = bundle["model"], bundle["features"], bundle["dtypes"]

print(dtypes)
