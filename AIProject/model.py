import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve, accuracy_score,
                              average_precision_score)
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("diabetes_dataset.csv")

df["Sex"] = df["Sex"].map({"Male": 0, "Female": 1})

print(f"Dataset shape: {df.shape}")
print(df["Outcome"].value_counts().rename({0: "No Diabetes", 1: "Diabetes"}))

zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
df[zero_cols] = df[zero_cols].replace(0, np.nan)
for col in zero_cols:
    df[col].fillna(df[col].median(), inplace=True)

features = [c for c in df.columns if c != "Outcome"]
X, y = df[features], df["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

fig, axes = plt.subplots(2, 4, figsize=(18, 8))
fig.suptitle("Feature Distributions by Diabetes Outcome", fontsize=14, fontweight="bold")
for ax, feat in zip(axes.flat, features):
    ax.hist(df[df.Outcome == 0][feat], bins=20, alpha=0.7, label="No Diabetes", color="#4F46E5")
    ax.hist(df[df.Outcome == 1][feat], bins=20, alpha=0.7, label="Diabetes",    color="#F97316")
    ax.set_title(feat, fontweight="bold")
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
axes.flat[0].legend()
plt.tight_layout()
plt.savefig("eda_distributions.png", dpi=120, bbox_inches="tight")
plt.show()
print("EDA plot saved → eda_distributions.png")

scale_pos = (y_train == 0).sum() / (y_train == 1).sum()

model = XGBClassifier(
    colsample_bytree=0.5,
    gamma=0.5,
    learning_rate=0.003,
    max_depth=2,
    min_child_weight=7,
    n_estimators=300,
    reg_alpha=0.1,
    reg_lambda=0.5,
    subsample=0.5,
    eval_metric='logloss',
    random_state=42,
    use_label_encoder=False
)
model.fit(X_train, y_train,
          eval_set=[(X_test, y_test)],
          verbose=False)

print("Model training complete!")

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("\n── Test Set Metrics ──────────────────────────────")
print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC-AUC  : {roc_auc_score(y_test, y_prob):.4f}")
print(f"Avg Prec : {average_precision_score(y_test, y_prob):.4f}")
print("\n── Classification Report ─────────────────────────")
print(classification_report(y_test, y_pred, target_names=["No Diabetes", "Diabetes"]))

cv_scores = cross_val_score(
    model, X, y,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring="roc_auc"
)
print(f"5-Fold CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

fig, axes = plt.subplots(1, 3, figsize=(17, 5))
fig.suptitle("XGBoost — Model Evaluation", fontsize=14, fontweight="bold")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["No Diab.", "Diabetes"],
            yticklabels=["No Diab.", "Diabetes"],
            ax=axes[0], cbar=False, annot_kws={"size": 13, "weight": "bold"})
axes[0].set_title("Confusion Matrix", fontweight="bold")
axes[0].set_xlabel("Predicted")
axes[0].set_ylabel("Actual")

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color="#4F46E5", lw=2.5,
             label=f"AUC = {roc_auc_score(y_test, y_prob):.3f}")
axes[1].plot([0, 1], [0, 1], "--", color="gray", lw=1.2)
axes[1].fill_between(fpr, tpr, alpha=0.1, color="#4F46E5")
axes[1].set_title("ROC Curve", fontweight="bold")
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")
axes[1].legend()

# Feature Importance
imp = pd.Series(model.feature_importances_, index=features).sort_values()
colors = ["#F97316" if v == imp.max() else "#4F46E5" for v in imp.values]
axes[2].barh(imp.index, imp.values, color=colors)
axes[2].set_title("Feature Importance (Gain)", fontweight="bold")
axes[2].set_xlabel("Importance Score")

plt.tight_layout()
plt.savefig("evaluation_report.png", dpi=120, bbox_inches="tight")
plt.show()
print("Evaluation plot saved → evaluation_report.png")


new_patients = pd.read_csv("new_patients_clean.csv")
new_patients["Sex"] = new_patients["Sex"].map({"Male": 0, "Female": 1})

probs = model.predict_proba(new_patients)[:, 1]
new_patients["DiabetesRisk%"] = (probs * 100).round(2)
new_patients["RiskLabel"] = new_patients["DiabetesRisk%"].apply(
    lambda p: "HIGH RISK" if p >= 50 else "LOW RISK"
)

# Decode Sex back for readability
new_patients["Sex"] = new_patients["Sex"].map({0: "Male", 1: "Female"})

print("\n── New Patient Predictions ───────────────────────")
print(new_patients[["Sex", "Age", "Glucose", "BMI", "DiabetesRisk%", "RiskLabel"]].to_string())

new_patients.to_csv("new_patients_predicted.csv", index=False)
print("\nPredictions saved → new_patients_predicted.csv")