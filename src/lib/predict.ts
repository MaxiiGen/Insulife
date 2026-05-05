import * as ort from "onnxruntime-web";

export const FEATURES = [
  "Pregnancies",
  "Glucose",
  "BloodPressure",
  "SkinThickness",
  "Insulin",
  "BMI",
  "DiabetesPedigreeFunction",
  "Age",
] as const;

export type FeatureKey = (typeof FEATURES)[number];
export type PatientInput = Record<FeatureKey, number>;

let sessionPromise: Promise<ort.InferenceSession | null> | null = null;

async function loadSession(): Promise<ort.InferenceSession | null> {
  if (!sessionPromise) {
    sessionPromise = (async () => {
      try {
        const res = await fetch("/model.onnx", { method: "HEAD" });
        if (!res.ok) return null;
        return await ort.InferenceSession.create("/model.onnx");
      } catch {
        return null;
      }
    })();
  }
  return sessionPromise;
}

// Heuristic fallback derived from clinical thresholds (Pima dataset). Used
// when no ONNX model is uploaded to /public/model.onnx.
function heuristicProbability(p: PatientInput): number {
  const z =
    -8.4 +
    0.123 * p.Pregnancies +
    0.0352 * p.Glucose +
    -0.0133 * p.BloodPressure +
    0.0006 * p.SkinThickness +
    -0.0012 * p.Insulin +
    0.0897 * p.BMI +
    0.945 * p.DiabetesPedigreeFunction +
    0.0149 * p.Age;
  return 1 / (1 + Math.exp(-z));
}

export interface PredictionResult {
  probability: number;
  label: "HIGH RISK" | "LOW RISK";
  source: "model" | "heuristic";
}

export async function predict(p: PatientInput): Promise<PredictionResult> {
  const session = await loadSession();
  let probability: number;
  let source: PredictionResult["source"] = "heuristic";

  if (session) {
    try {
      const data = Float32Array.from(FEATURES.map((f) => p[f]));
      const tensor = new ort.Tensor("float32", data, [1, FEATURES.length]);
      const inputName = session.inputNames[0];
      const out = await session.run({ [inputName]: tensor });
      const first = out[session.outputNames[0]].data as Float32Array;
      // XGBoost binary classifiers typically output [prob_class_1] or [p0,p1]
      probability = first.length === 1 ? first[0] : first[1];
      source = "model";
    } catch {
      probability = heuristicProbability(p);
    }
  } else {
    probability = heuristicProbability(p);
  }

  return {
    probability,
    label: probability >= 0.5 ? "HIGH RISK" : "LOW RISK",
    source,
  };
}

export async function predictBatch(rows: PatientInput[]) {
  return Promise.all(rows.map(predict));
}
