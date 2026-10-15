import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

bundle = joblib.load("./models/model.joblib")
features = bundle["features"]


# class User(BaseModel):

app = FastAPI()

@app.get("/score")
def score():
    approved = np.random.choice([True, False])
    return {"approved": bool(approved)}


