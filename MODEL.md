Place your trained model as `model.pkl` in the repository root.

Model requirements:
- The model must be a pickled object (created via `pickle.dump`) that implements `predict_proba(X)`.
- `X` should be a 2D table (pandas DataFrame or 2D numpy array) with columns (order not strictly required if DataFrame is provided):
  - Age
  - Sex (string or numeric — app maps common strings to numeric)
  - Glucose
  - BMI
  - BloodPressure
  - Insulin
  - SkinThickness
  - DiabetesPedigreeFunction

How the app works:
- Single-patient mode: enter values manually and press `Predict` to get a probability (%) and HIGH/LOW risk label.
- Bulk mode: upload a CSV with the above columns; the app will output a table with `DiabetesProbability` and `RiskLabel` and allow CSV download.

Run locally:
1. Create a Python environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Place `model.pkl` in the repo root.

3. Run Streamlit:

```bash
streamlit run app.py
```

Notes:
- The app treats probabilities >= 50% as `HIGH RISK`.
- If your model uses a different column set/order, adapt the `EXPECTED_COLUMNS` in `app.py` or export your model accordingly.
