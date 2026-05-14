export const FEATURES = [
  "Age",
  "Sex",
  "Glucose",
  "BMI",
  "BloodPressure",
  "Insulin",
  "SkinThickness",
  "DiabetesPedigreeFunction",
] as const;

export type FeatureKey = (typeof FEATURES)[number];
export type PatientInput = Record<FeatureKey, number | string>;

export interface PredictionResult {
  probability: number;
  label: "HIGH RISK" | "LOW RISK";
  source: "model";
  probabilityPercent?: number;
}

export async function predict(p: PatientInput): Promise<PredictionResult> {
  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient: p }),
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error ?? "Prediction failed.");
  }

  return data;
}

export async function predictBatch(rows: PatientInput[]) {
  const response = await fetch("/api/predict-batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patients: rows }),
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error ?? "Batch prediction failed.");
  }

  return data.results as PredictionResult[];
}
