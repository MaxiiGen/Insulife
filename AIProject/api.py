from flask import Flask, jsonify, request
import pandas as pd

from app import EXPECTED_COLUMNS, RISK_THRESHOLD, load_model, normalize_columns, predict_dataframe


app = Flask(__name__)


def model_unavailable_response():
    return (
        jsonify(
            {
                "error": "Model not loaded. Place model.pkl in the repository root and restart the API.",
            }
        ),
        503,
    )


def result_rows(results: pd.DataFrame):
    rows = []
    for record in results.to_dict(orient="records"):
        probability_percent = float(record["DiabetesProbability"])
        rows.append(
            {
                "input": {column: record.get(column) for column in EXPECTED_COLUMNS},
                "probability": probability_percent / 100,
                "probabilityPercent": probability_percent,
                "label": record["RiskLabel"],
                "source": "model",
            }
        )
    return rows


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "modelLoaded": load_model() is not None})


@app.get("/api/model-info")
def model_info():
    return jsonify(
        {
            "modelLoaded": load_model() is not None,
            "features": EXPECTED_COLUMNS,
            "threshold": RISK_THRESHOLD,
            "supports": ["single-patient", "bulk-csv"],
        }
    )


@app.post("/api/predict")
def predict_single():
    model = load_model()
    if model is None:
        return model_unavailable_response()

    payload = request.get_json(silent=True) or {}
    patient = payload.get("patient", payload)
    if not isinstance(patient, dict):
        return jsonify({"error": "Expected a patient object."}), 400

    try:
        frame = normalize_columns(pd.DataFrame([patient]))
        results = predict_dataframe(model, frame)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result_rows(results)[0])


@app.post("/api/predict-batch")
def predict_batch():
    model = load_model()
    if model is None:
        return model_unavailable_response()

    payload = request.get_json(silent=True) or {}
    patients = payload.get("patients", payload.get("rows"))
    if not isinstance(patients, list):
        return jsonify({"error": "Expected a patients array."}), 400
    if not patients:
        return jsonify({"error": "At least one patient row is required."}), 400

    try:
        frame = normalize_columns(pd.DataFrame(patients))
        results = predict_dataframe(model, frame)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"results": result_rows(results)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
