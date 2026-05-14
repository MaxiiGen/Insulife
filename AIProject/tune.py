#!/usr/bin/env python3
"""
XGBoost Hyperparameter Tuning v3 — Expanded GridSearchCV
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# LOAD & PREPROCESS
# ──────────────────────────────────────────────────────────────────────────────
df = pd.read_csv("diabetes_dataset.csv")
df["Sex"] = df["Sex"].map({"Male": 0, "Female": 1})

zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
df[zero_cols] = df[zero_cols].replace(0, np.nan)
for col in zero_cols:
    df[col].fillna(df[col].median(), inplace=True)

features = [c for c in df.columns if c != "Outcome"]
X, y = df[features], df["Outcome"]

# ──────────────────────────────────────────────────────────────────────────────
# EXPANDED GRID
# ──────────────────────────────────────────────────────────────────────────────
param_grid = {
    "n_estimators":     [300, 500, 700, 1000],
    "max_depth":        [2, 3, 4, 5],
    "learning_rate":    [0.003, 0.005, 0.01, 0.03],
    "subsample":        [0.5, 0.6, 0.7, 0.8],
    "colsample_bytree": [0.5, 0.6, 0.7, 0.8],
    "min_child_weight": [3, 5, 7, 10],
    "reg_alpha":        [0, 0.1, 0.5, 1.0],
    "reg_lambda":       [0.5, 1, 1.5, 2],
    "gamma":            [0, 0.1, 0.3, 0.5],
}

model = XGBClassifier(
    eval_metric="logloss",
    random_state=42,
    use_label_encoder=False
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("Running expanded GridSearchCV v3...")
print("⚠️  This will take a while — go grab a snack 🍕")
grid = GridSearchCV(
    model,
    param_grid,
    cv=cv,
    scoring="roc_auc",
    n_jobs=-1,
    verbose=1
)
grid.fit(X, y)

# ──────────────────────────────────────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────────────────────────────────────
print("\n── Best Parameters ───────────────────────────────")
for k, v in grid.best_params_.items():
    print(f"  {k}: {v}")

print(f"\n── Best CV AUC: {grid.best_score_:.4f} ──────────────")

print("\n── Copy these into model.py ──────────────────────")
print("model = XGBClassifier(")
for k, v in grid.best_params_.items():
    val = f'"{v}"' if isinstance(v, str) else v
    print(f"    {k}={val},")
print("    eval_metric='logloss',")
print("    random_state=42,")
print("    use_label_encoder=False")
print(")")