import unittest
import pandas as pd

from app import EXPECTED_COLUMNS, normalize_columns, predict_dataframe


class DummyModel:
    def predict_proba(self, X):
        # Return a deterministic high/low mix for test assertions.
        return pd.DataFrame({0: [0.2, 0.8], 1: [0.8, 0.2]}).to_numpy()


class AppHelperTests(unittest.TestCase):
    def test_normalize_columns_maps_common_names(self):
        frame = pd.DataFrame(
            {
                "age": [30],
                "sex": ["Male"],
                "glucose": [140],
                "bmi": [31.2],
                "blood_pressure": [80],
                "insulin": [90],
                "skin thickness": [22],
                "diabetes pedigree function": [0.42],
            }
        )

        normalized = normalize_columns(frame)

        self.assertEqual(list(normalized.columns), EXPECTED_COLUMNS)

    def test_predict_dataframe_adds_probability_and_label(self):
        frame = pd.DataFrame(
            [
                {
                    "Age": 30,
                    "Sex": "Male",
                    "Glucose": 140,
                    "BMI": 31.2,
                    "BloodPressure": 80,
                    "Insulin": 90,
                    "SkinThickness": 22,
                    "DiabetesPedigreeFunction": 0.42,
                },
                {
                    "Age": 45,
                    "Sex": "Female",
                    "Glucose": 95,
                    "BMI": 24.1,
                    "BloodPressure": 70,
                    "Insulin": 70,
                    "SkinThickness": 18,
                    "DiabetesPedigreeFunction": 0.12,
                },
            ]
        )

        results = predict_dataframe(DummyModel(), frame)

        self.assertIn("DiabetesProbability", results.columns)
        self.assertIn("RiskLabel", results.columns)
        self.assertEqual(results.loc[0, "DiabetesProbability"], 80.0)
        self.assertEqual(results.loc[0, "RiskLabel"], "HIGH RISK")
        self.assertEqual(results.loc[1, "DiabetesProbability"], 20.0)
        self.assertEqual(results.loc[1, "RiskLabel"], "LOW RISK")

    def test_predict_dataframe_rejects_missing_columns(self):
        frame = pd.DataFrame(
            [
                {
                    "Age": 30,
                    "Sex": "Male",
                    "Glucose": 140,
                    "BMI": 31.2,
                }
            ]
        )

        with self.assertRaises(ValueError):
            predict_dataframe(DummyModel(), frame)


if __name__ == "__main__":
    unittest.main()
