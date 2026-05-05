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
export type PatientInput = Record<FeatureKey, number>;

export interface PredictionResult {
  probability: number;
  label: "HIGH RISK" | "LOW RISK";
  source: "model";
}

function getApiUrl(): string {
  // In browser, use the environment variable set at build time
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  // Fallback for SSR
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

export async function predict(p: PatientInput): Promise<PredictionResult> {
  try {
    const apiUrl = getApiUrl();
    const response = await fetch(`${apiUrl}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    });
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Prediction failed: ${error}`);
    }
    const data = await response.json();
    return {
      probability: data.probability / 100,
      label: data.label,
      source: "model",
    };
  } catch (error) {
    console.error("Prediction error:", error);
    throw error;
  }
}

export async function predictBatch(rows: PatientInput[]) {
  try {
    const apiUrl = getApiUrl();
    const response = await fetch(`${apiUrl}/api/predict-bulk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ records: rows }),
    });
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Bulk prediction failed: ${error}`);
    }
    const data = await response.json();
    return data.map((item: any) => ({
      probability: item.probability / 100,
      label: item.label,
      source: "model",
    }));
  } catch (error) {
    console.error("Bulk prediction error:", error);
    throw error;
  }
}
