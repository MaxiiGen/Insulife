import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { predict, PredictionResult, FEATURES, PatientInput } from "@/lib/predict";
import { Loader2, Sparkles } from "lucide-react";

const FIELDS: { key: keyof PatientInput; label: string; step?: string; placeholder: string }[] = [
  { key: "Age", label: "Age (years)", placeholder: "e.g. 35" },
  { key: "Sex", label: "Sex (0=Female, 1=Male)", placeholder: "e.g. 1" },
  { key: "Glucose", label: "Glucose (mg/dL)", placeholder: "e.g. 120" },
  { key: "BMI", label: "BMI", step: "0.1", placeholder: "e.g. 28.5" },
  { key: "BloodPressure", label: "Blood Pressure (mm Hg)", placeholder: "e.g. 70" },
  { key: "Insulin", label: "Insulin (μU/mL)", placeholder: "e.g. 80" },
  { key: "SkinThickness", label: "Skin Thickness (mm)", placeholder: "e.g. 20" },
  { key: "DiabetesPedigreeFunction", label: "Diabetes Pedigree", step: "0.001", placeholder: "e.g. 0.471" },
];

const DEFAULTS: PatientInput = {
  Age: 35,
  Sex: 1,
  Glucose: 120,
  BMI: 28.5,
  BloodPressure: 70,
  Insulin: 80,
  SkinThickness: 20,
  DiabetesPedigreeFunction: 0.471,
};

export const SinglePatientForm = () => {
  const [values, setValues] = useState<PatientInput>(DEFAULTS);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const r = await predict(values);
    setResult(r);
    setLoading(false);
  };

  return (
    <div className="grid gap-8 md:grid-cols-[1.3fr_1fr]">
      <form onSubmit={onSubmit} className="rounded-[var(--radius)] bg-card p-8 shadow-[var(--shadow-card)]">
        <div className="grid gap-5 sm:grid-cols-2">
          {FIELDS.map((f) => (
            <div key={f.key} className="space-y-2">
              <Label htmlFor={f.key} className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {f.label}
              </Label>
              <Input
                id={f.key}
                type="number"
                step={f.step ?? "1"}
                placeholder={f.placeholder}
                value={values[f.key]}
                onChange={(e) =>
                  setValues({ ...values, [f.key]: parseFloat(e.target.value) || 0 })
                }
                className="h-12 rounded-xl border-border bg-background"
                required
              />
            </div>
          ))}
        </div>
        <Button type="submit" variant="hero" size="lg" className="mt-8 w-full" disabled={loading}>
          {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          Classify Risk
        </Button>
      </form>

      <ResultPanel result={result} />
    </div>
  );
};

const ResultPanel = ({ result }: { result: PredictionResult | null }) => {
  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center rounded-[var(--radius)] bg-[image:var(--gradient-hero)] p-10 text-center text-primary-foreground shadow-[var(--shadow-soft)]">
        <p className="font-display text-3xl leading-tight">Awaiting<br />patient data</p>
        <p className="mt-3 text-sm opacity-80">Fill the form to compute a diabetes risk score.</p>
      </div>
    );
  }

  const pct = (result.probability * 100).toFixed(1);
  const isHigh = result.label === "HIGH RISK";

  return (
    <div className="flex flex-col items-center justify-center rounded-[var(--radius)] bg-[image:var(--gradient-hero)] p-10 text-primary-foreground shadow-[var(--shadow-soft)]">
      <p className="text-xs uppercase tracking-[0.25em] opacity-70">Risk Probability</p>
      <p className="font-display text-7xl font-bold leading-none mt-3">{pct}%</p>
      <div
        className="mt-6 rounded-full px-6 py-2 text-sm font-bold tracking-wider"
        style={{ background: isHigh ? "hsl(var(--risk-high))" : "hsl(var(--risk-low))" }}
      >
        {result.label}
      </div>
      <p className="mt-6 text-xs opacity-60">
        Source: {result.source === "model" ? "XGBoost ONNX model" : "Heuristic baseline"}
      </p>
    </div>
  );
};
