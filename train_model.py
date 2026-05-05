import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import pickle

# Load Pima Indians dataset from a URL
URL = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"

df = pd.read_csv(URL)
# Expected columns in this CSV: 'Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigreeFunction','Age','Outcome'
# We'll map to our expected schema
y = df['Outcome']

mapping = {
    'Age': 'Age',
    'Glucose': 'Glucose',
    'BMI': 'BMI',
    'BloodPressure': 'BloodPressure',
    'Insulin': 'Insulin',
    'SkinThickness': 'SkinThickness',
    'DiabetesPedigreeFunction': 'DiabetesPedigreeFunction',
}

EXPECTED_COLUMNS = [
    'Age',
    'Sex',
    'Glucose',
    'BMI',
    'BloodPressure',
    'Insulin',
    'SkinThickness',
    'DiabetesPedigreeFunction',
]

X = df[list(mapping.keys())].rename(columns=mapping)
y = df['Outcome']

# Add Sex column as random (since dataset lacks sex) and reorder to EXPECTED_COLUMNS
np.random.seed(0)
X['Sex'] = np.random.choice([0,1], size=len(X))
X = X[EXPECTED_COLUMNS]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print('Saved model to model.pkl')
