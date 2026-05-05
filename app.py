import streamlit as st
import pandas as pd
import pickle
import os

MODEL_PATH = "model.pkl"
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

@st.cache_resource
def load_model(path=MODEL_PATH):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize incoming CSV columns to the expected set (case-insensitive, simple heuristics)
    def canonical(name: str) -> str:
        return "".join(ch for ch in name.lower().strip() if ch.isalnum())

    cols = {canonical(c): c for c in df.columns}
    mapping = {}
    for expected in EXPECTED_COLUMNS:
        el = canonical(expected)
        if el in cols:
            mapping[cols[el]] = expected
            continue
        # heuristics
        for k, orig in cols.items():
            if el in k or k in el:
                mapping[orig] = expected
                break
        else:
            # try common synonyms
            if el == "bloodpressure":
                for k, orig in cols.items():
                    if "blood" in k and ("pressure" in k or "bp" in k):
                        mapping[orig] = "BloodPressure"
                        break
    if mapping:
        df = df.rename(columns=mapping)
    return df


def predict_dataframe(model, df: pd.DataFrame) -> pd.DataFrame:
    X = df.copy()
    # Ensure columns exist
    missing = [c for c in EXPECTED_COLUMNS if c not in X.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    X = X[EXPECTED_COLUMNS]
    # Map Sex to numeric if needed
    if X["Sex"].dtype == object:
        X["Sex"] = X["Sex"].str.lower().map({"male": 1, "m": 1, "female": 0, "f": 0}).fillna(-1).astype(int)
    else:
        X["Sex"] = X["Sex"].astype(int)
    # Predict
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[:, 1]
    elif hasattr(model, "predict"):
        preds = model.predict(X)
        probs = preds.astype(float)
    else:
        raise ValueError("Loaded model does not support predict_proba or predict")
    out = df.copy()
    out["DiabetesProbability"] = (probs * 100).round(2)
    out["RiskLabel"] = out["DiabetesProbability"].apply(lambda p: "HIGH RISK" if p >= 50 else "LOW RISK")
    return out


def main():
    st.set_page_config(page_title="Diabetes Risk Classifier", layout="centered")
    st.title("Diabetes Risk Classification")

    model = load_model()
    if model is None:
        st.warning(f"No model found at {MODEL_PATH}. Place a trained model file named model.pkl in the repository root.")

    mode = st.radio("Mode", ["Single patient", "Bulk upload (CSV)"])

    if mode == "Single patient":
        st.subheader("Enter patient clinical values")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            sex = st.selectbox("Sex", ["Female", "Male", "Other"])
            glucose = st.number_input("Glucose", min_value=0.0, value=120.0)
            bmi = st.number_input("BMI", min_value=0.0, value=25.0)
        with col2:
            blood_pressure = st.number_input("BloodPressure", min_value=0.0, value=70.0)
            insulin = st.number_input("Insulin", min_value=0.0, value=80.0)
            skin_thickness = st.number_input("SkinThickness", min_value=0.0, value=20.0)
            dpf = st.number_input("DiabetesPedigreeFunction", min_value=0.0, value=0.5)

        if st.button("Predict"):
            sex_map = {"Female": 0, "Male": 1, "Other": -1}
            row = pd.DataFrame([{
                "Age": age,
                "Sex": sex_map.get(sex, -1),
                "Glucose": glucose,
                "BMI": bmi,
                "BloodPressure": blood_pressure,
                "Insulin": insulin,
                "SkinThickness": skin_thickness,
                "DiabetesPedigreeFunction": dpf,
            }])
            try:
                if model is None:
                    st.error("Model not loaded. Place `model.pkl` in repo root and refresh.")
                else:
                    out = predict_dataframe(model, row)
                    prob = out.loc[0, "DiabetesProbability"]
                    label = out.loc[0, "RiskLabel"]
                    st.metric(label=f"Risk: {label}", value=f"{prob}%")
                    st.write(out)
            except Exception as e:
                st.error(str(e))

    else:
        st.subheader("Upload CSV with patient rows")
        uploaded = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
            except Exception as e:
                st.error("Could not read CSV: " + str(e))
                return
            df = normalize_columns(df)
            missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
            if missing:
                st.error(f"CSV is missing required columns: {missing}")
                st.info(f"Expected columns: {EXPECTED_COLUMNS}")
                return
            if model is None:
                st.error("Model not loaded. Place `model.pkl` in repo root and refresh.")
                return
            try:
                results = predict_dataframe(model, df)
            except Exception as e:
                st.error(str(e))
                return
            st.success("Prediction complete")
            st.dataframe(results)
            csv = results.to_csv(index=False).encode("utf-8")
            st.download_button("Download results as CSV", data=csv, file_name="predictions.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Model expectations: the repository should contain a pickled sklearn/xgboost classifier named `model.pkl` that implements `predict_proba(X)` and accepts a tabular input with columns: " + ", ".join(EXPECTED_COLUMNS))


if __name__ == "__main__":
    main()
