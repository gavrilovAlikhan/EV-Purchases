# EV Purchases

A made-up government EV grant scenario, built on Kaggle data, that predicts and explains whether an applicant will buy an electric vehicle.

## Quick background

Kaggle competitions are a fun way to practise, but they can get repetitive. A lot of the work comes down to leaderboard tricks, reverse-engineering the synthetic data generator, and feature engineering that has little to do with how real production ML projects are built. 

So I decided to build a fictional scenario around the data from a Kaggle [Playground Series S6E9](https://www.kaggle.com/competitions/playground-series-s6e9) competition.

**The scenario I came up with:** A government EV grant programme ran a pilot in one region, and take-up was disappointing. That pilot's data is used to train the model. The programme is now being rerun in a new region, and the aim is to find the applicants most likely to actually buy an EV.

**The app:** A promo-style form where a member of the public registers interest in the grant. When they submit it, the model scores how likely they are to buy an EV.

**Data adjustments:**
- **Removed gender** so that protected characteristics don't drive grant decisions, which avoids fairness and legal concerns.
- **Postcode lookup:** Applicants enter a postcode rather than describing their area. City type and the number of nearby charging stations are derived from it, the way a real system would get them.

**AI slop?**
This project isn't vibecoded. I built it to practise real-world ML problems, though of course I used AI to help along the way. I wrote all the logic and scripts myself. The only part I mostly outsourced to Claude was redesigning the form's UI in `app.py`, because I needed it to look nice (check my earliest commits to see how shit the form looked when I built it myself).

>However, this isn't meant to be a state-of-the-art production-grade repo (I'm still learning ML myself and there is plenty to improve), but it was useful practice in how real-world ML differs from competition work.

## Overview

The project trains a **LightGBM** classifier on the Kaggle
[Playground Series S6E9](https://www.kaggle.com/competitions/playground-series-s6e9) dataset,
serves it with a **FastAPI** backend, and puts a **Streamlit** form in front of it.
The form shows the purchase probability and a **SHAP** waterfall chart of the features
that drove the prediction.

```text
┌──────────────────┐   HTTP    ┌──────────────────────┐
│  Streamlit UI    │ ────────▶ │  FastAPI service     │
│  frontend/app.py │ ◀──────── │  ev_purchases.service│
│  :8501           │   JSON    │  :8000               │
└──────────────────┘           └──────────┬───────────┘
                                          │ loads
                               ┌──────────┴───────────┐
                               │ models/model.joblib   │
                               │ data/raw/train.csv    │
                               └───────────────────────┘
```

---

## Project structure

```text
EV-Purchases/
├── backend/src/ev_purchases/
│   ├── get_data.py              # downloads the Kaggle competition data
│   ├── train.py                 # trains the LightGBM model and saves it
│   ├── service.py               # FastAPI app (/postcodes, /score, /explain)
│   ├── feature_engineering.py   # feature pipeline shared by training and serving
│   ├── data_loader.py
│   └── utils/generate_postcode_lookup.py  # synthetic postcode → charging station lookup
├── frontend/app.py              # Streamlit UI
├── configs/train.yaml           # model hyperparameters and data settings
├── data/raw/                    # Kaggle CSVs land here
├── models/                      # trained model bundles (.joblib)
├── notebooks/                   # EDA, feature synthesis, training experiments
├── Dockerfile / compose.yaml    # containerised API + UI
├── pyproject.toml / uv.lock
└── .env_example
```

---

## Prerequisites

- **Python 3.14** (pinned in `.python-version`)
- **[uv](https://docs.astral.sh/uv/)** for managing dependencies
- A **Kaggle account**

---

## Getting started

> Run **all** commands from the project root (the folder that contains `pyproject.toml`).
> The scripts use paths relative to it.

### 1. Install dependencies

```bash
uv sync
```

This creates `.venv/` and installs the `ev_purchases` package along with everything
it depends on. Every command below uses `uv run`, so you don't need to activate the
environment yourself.

### 2. Get a Kaggle API token and join the competition

The dataset is part of a Kaggle competition, so you need **both** of these before you
can download it:

1. **Create an API token.** On Kaggle, open **Settings → API** and click
   **Create New Token**. Copy the token value.
2. **Join the competition.** Open
   <https://www.kaggle.com/competitions/playground-series-s6e9>, click **Join Competition**
   and accept the rules.
   *If you skip this, the download fails with a `403 Forbidden` error.*

Then create your `.env` file from the example and paste in the token:

```dotenv
# .env
KAGGLE_API_TOKEN="KGAT_your_token_here"
```

> `.env` is git-ignored, so your token never gets committed.

### 3. Download the data

```bash
uv run python -m ev_purchases.get_data
```

This downloads the competition files and unzips them into `data/raw/`:

```text
data/raw/
├── train.csv
├── test.csv
└── sample_submission.csv
```

### 4. Train the model (train.py)

```bash
uv run python -m ev_purchases.train
```

Training uses the hyperparameters in `configs/train.yaml` and prints the log-loss
every 300 iterations. The model bundle (model, feature order and dtypes) is saved to
`models/model.joblib`, which is the file the API loads.

### 5. Start the FastAPI backend

Start the API **first**, because the Streamlit app asks it for the postcode list as
soon as it loads.

```bash
uv run uvicorn ev_purchases.service:app --reload --port 8000
```

When you see `Application startup complete`, the API is ready. Interactive docs are
at <http://127.0.0.1:8000/docs>.

### 6. Start the Streamlit frontend

Open a **second terminal** in the project root and run:

```bash
uv run streamlit run frontend/app.py
```

Streamlit opens <http://localhost:8501> in your browser. Fill in the form and click
**Check eligibility** to see the prediction and the SHAP explanation.

The frontend calls `http://127.0.0.1:8000` by default. To use a different backend,
set the `API_URL` environment variable:

```bash
API_URL=http://my-api-host:8000 uv run streamlit run frontend/app.py
```

---

## API endpoints

| Method | Path         | Description                                                        |
|--------|--------------|--------------------------------------------------------------------|
| `GET`  | `/postcodes` | Lists the available home and work postcodes                        |
| `POST` | `/score`     | Returns the purchase probability and an approved/not-approved flag |
| `POST` | `/explain`   | Returns the SHAP base value and per-feature contributions          |

Example request body for `/score` and `/explain`:

```json
{
  "age": 35,
  "income": 85000,
  "daily_commute": 25,
  "cars": 1,
  "concern": 4,
  "home_charging": true,
  "range_anxiety": "Low",
  "current_car": "Sedan",
  "subsidy": false,
  "home_postcode": "1AB 2CD",
  "work_postcode": "3EF 4GH"
}
```

> Postcodes are **synthetic**. They are generated with a fixed random seed when the
> service starts, so get valid values from `GET /postcodes`. The example values above
> are placeholders and won't be found.

---

## Running with Docker (optional)

Steps 1–4 above (data download and training) still have to run on your
machine first. The image copies in `data/raw/train.csv` and `models/model.joblib`
at build time, and the API needs both to start.

```bash
docker compose up --build
```

- API: <http://localhost:8000/docs>
- UI: <http://localhost:8501>

The UI container waits until the API passes its health check before it starts.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `403 Forbidden` when downloading data | Join the competition and accept its rules on Kaggle (step 2). |
| `401 Unauthorized` / Kaggle authentication error | Check that `KAGGLE_API_TOKEN` in `.env` is set and correct. |
| `'data/raw/train.csv' is not found` | Run the data download (step 3) from the project root. |
| API fails with `FileNotFoundError: ... model.joblib` | Train the model (step 4) from the project root. |
| Streamlit shows `ConnectionError` on load | Start the FastAPI backend first (step 5), then refresh the page. |
| `ModuleNotFoundError: No module named 'ev_purchases'` | Run `uv sync`, and run commands with `uv run` from the project root. |
