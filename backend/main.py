import pickle
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

app = FastAPI()

# CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.getenv("MODEL_PATH", "model.pkl")

EXPECTED_COLUMNS = [
    "Age",
    "Sex",
    "Glucose",
    "BMI",
    "BloodPressure",
    "Insulin",
    "SkinThickness",
    "DiabetesPedigreeFunction",
]


@app.on_event("startup")
def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model file not found at {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"Model loaded from {MODEL_PATH}")


class PatientRecord(BaseModel):
    Age: float
    Sex: int
    Glucose: float
    BMI: float
    BloodPressure: float
    Insulin: float
    SkinThickness: float
    DiabetesPedigreeFunction: float


class PredictionResponse(BaseModel):
    probability: float
    label: str


class BulkPredictionRequest(BaseModel):
    records: list[PatientRecord]


@app.post("/api/predict", response_model=PredictionResponse)
def predict_single(patient: PatientRecord):
    try:
        df = pd.DataFrame([patient.model_dump()])
        df = df[EXPECTED_COLUMNS]
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(df)[:, 1][0]
        else:
            prob = model.predict(df)[0]
        prob_percent = float(prob) * 100
        label = "HIGH RISK" if prob_percent >= 50 else "LOW RISK"
        return PredictionResponse(probability=prob_percent, label=label)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict-bulk", response_model=list[dict])
def predict_bulk(request: BulkPredictionRequest):
    try:
        data = [r.model_dump() for r in request.records]
        df = pd.DataFrame(data)
        df = df[EXPECTED_COLUMNS]
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(df)[:, 1]
        else:
            probs = model.predict(df)
        results = []
        for i, prob in enumerate(probs):
            prob_percent = float(prob) * 100
            label = "HIGH RISK" if prob_percent >= 50 else "LOW RISK"
            results.append({**data[i], "probability": prob_percent, "label": label})
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok"}
