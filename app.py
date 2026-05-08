import streamlit as st
import pandas as pd
import pickle
import os
from typing import Iterable

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

DISPLAY_COLUMNS = {
    "Age": "Age",
    "Sex": "Sex",
    "Glucose": "Glucose",
    "BMI": "BMI",
    "BloodPressure": "Blood Pressure",
    "Insulin": "Insulin",
    "SkinThickness": "Skin Thickness",
    "DiabetesPedigreeFunction": "Diabetes Pedigree Function",
}

SEX_MAP = {
    "male": 1,
    "m": 1,
    "1": 1,
    1: 1,
    "female": 0,
    "f": 0,
    "0": 0,
    0: 0,
}

@st.cache_resource
def load_model(path=MODEL_PATH):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model


def canonical(name: str) -> str:
    return "".join(ch for ch in str(name).lower().strip() if ch.isalnum())


def normalize_sex(value):
    if pd.isna(value):
        return value
    if isinstance(value, str):
        key = value.strip().lower()
        if key in SEX_MAP:
            return SEX_MAP[key]
        if key.isdigit() and int(key) in SEX_MAP:
            return SEX_MAP[int(key)]
        return value
    if value in SEX_MAP:
        return SEX_MAP[value]
    return value


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
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
    space_aliases = {
        "bloodpressure": "BloodPressure",
        "skinthickness": "SkinThickness",
        "diabetespedigreefunction": "DiabetesPedigreeFunction",
    }
    extra_mapping = {}
    for column in df.columns:
        key = canonical(column)
        if key in space_aliases and column != space_aliases[key]:
            extra_mapping[column] = space_aliases[key]
    if extra_mapping:
        df = df.rename(columns=extra_mapping)
    return df


def coerce_model_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    missing = [column for column in EXPECTED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame["Sex"] = frame["Sex"].map(normalize_sex)
    frame["Sex"] = pd.to_numeric(frame["Sex"], errors="coerce")
    if frame["Sex"].isna().any():
        raise ValueError("Sex must be one of Male/Female or 1/0")

    for column in EXPECTED_COLUMNS:
        if column == "Sex":
            continue
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise ValueError(f"Column {column} must contain numeric values")

    return frame[EXPECTED_COLUMNS]


def format_probability(probability: float) -> str:
    return f"{probability:.2f}%"


def predict_dataframe(model, df: pd.DataFrame) -> pd.DataFrame:
    X = coerce_model_frame(df)

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


def display_single_result(probability: float, label: str) -> None:
    st.metric("Diabetes risk", format_probability(probability))
    st.markdown(
        f"<div style='font-size:1.25rem;font-weight:700;margin-top:0.5rem;'>Classification: {label}</div>",
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="Diabetes Risk Classification", layout="centered")
    st.title("Diabetes Risk Classification")
    st.write(
        "Enter the eight clinical values manually for one patient or upload a CSV for batch scoring. "
        "The app loads the pickled model from `model.pkl` in the repository root."
    )

    model = load_model()
    if model is None:
        st.warning(
            f"No model found at {MODEL_PATH}. Place a trained model file named model.pkl in the repository root."
        )

    mode = st.tabs(["Single patient", "Bulk upload"])

    with mode[0]:
        st.subheader("Enter patient clinical values")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            sex = st.selectbox("Sex", ["Female", "Male"])
            glucose = st.number_input("Glucose", min_value=0.0, value=120.0)
            bmi = st.number_input("BMI", min_value=0.0, value=25.0)
        with col2:
            blood_pressure = st.number_input("Blood Pressure", min_value=0.0, value=70.0)
            insulin = st.number_input("Insulin", min_value=0.0, value=80.0)
            skin_thickness = st.number_input("Skin Thickness", min_value=0.0, value=20.0)
            dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, value=0.5)

        if st.button("Predict"):
            row = pd.DataFrame([{
                "Age": age,
                "Sex": 1 if sex == "Male" else 0,
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
                    display_single_result(prob, label)
                    st.dataframe(out, use_container_width=True)
            except Exception as e:
                st.error(str(e))

    with mode[1]:
        st.subheader("Upload CSV with patient rows")
        st.caption("Required columns: Age, Sex, Glucose, BMI, Blood Pressure, Insulin, Skin Thickness, Diabetes Pedigree Function")
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
                st.info(
                    "Expected columns: Age, Sex, Glucose, BMI, Blood Pressure, Insulin, Skin Thickness, Diabetes Pedigree Function"
                )
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
            display_results = results.copy()
            display_results["DiabetesProbability"] = display_results["DiabetesProbability"].map(lambda p: f"{p:.2f}%")
            st.dataframe(display_results, use_container_width=True)
            csv = results.to_csv(index=False).encode("utf-8")
            st.download_button("Download results as CSV", data=csv, file_name="predictions.csv", mime="text/csv")

    st.markdown("---")
    st.markdown(
        "Model expectations: the repository should contain a pickled sklearn/xgboost classifier named `model.pkl` that implements `predict_proba(X)` and accepts a tabular input with columns: "
        + ", ".join(EXPECTED_COLUMNS)
    )


if __name__ == "__main__":
    main()
