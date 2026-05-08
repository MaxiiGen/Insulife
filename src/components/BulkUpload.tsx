import { useState } from "react";
import Papa from "papaparse";
import { Button } from "@/components/ui/button";
import { predictBatch, FEATURES, PatientInput, PredictionResult } from "@/lib/predict";
import { Upload, Download, Loader2, FileSpreadsheet } from "lucide-react";

interface Row extends PatientInput {
  __result?: PredictionResult;
}

export const BulkUpload = () => {
  const [rows, setRows] = useState<Row[]>([]);
  const [filename, setFilename] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const onFile = (file: File) => {
    setError("");
    setFilename(file.name);
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: async (res) => {
        const parsed = (res.data as Record<string, unknown>[]).map((r) => {
          const out: Partial<PatientInput> = {};
          for (const f of FEATURES) out[f] = Number(r[f] ?? 0);
          return out as PatientInput;
        });
        if (!parsed.length) {
          setError("No rows found. CSV must include columns: " + FEATURES.join(", "));
          return;
        }
        setLoading(true);
        const results = await predictBatch(parsed);
        setRows(parsed.map((p, i) => ({ ...p, __result: results[i] })));
        setLoading(false);
      },
    });
  };

  const downloadCSV = () => {
    const data = rows.map((r) => {
      const base: Record<string, unknown> = {};
      FEATURES.forEach((f) => (base[f] = r[f]));
      base.RiskProbability = r.__result ? (r.__result.probability * 100).toFixed(2) + "%" : "";
      base.Classification = r.__result?.label ?? "";
      return base;
    });
    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "diabetes_predictions.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadTemplate = () => {
    const csv = Papa.unparse([Object.fromEntries(FEATURES.map((f) => [f, 0]))]);
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "patients_template.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="rounded-[var(--radius)] bg-card p-8 shadow-[var(--shadow-card)]">
        <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-border bg-muted/40 p-12 text-center">
          <FileSpreadsheet className="mb-4 h-12 w-12 text-primary" />
          <p className="font-display text-2xl">Upload patient CSV</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Required columns: {FEATURES.join(", ")}
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <label>
              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
              />
              <Button asChild variant="hero" size="lg">
                <span className="cursor-pointer">
                  <Upload className="mr-2 h-4 w-4" /> Choose CSV
                </span>
              </Button>
            </label>
            <Button type="button" variant="outline" size="lg" onClick={downloadTemplate}>
              Download template
            </Button>
          </div>
          {filename && (
            <p className="mt-4 text-xs text-muted-foreground">Loaded: {filename}</p>
          )}
          {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Scoring patients…
        </div>
      )}

      {rows.length > 0 && !loading && (
        <div className="rounded-[var(--radius)] bg-card p-6 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <p className="font-display text-2xl">{rows.length} patients scored</p>
            <Button onClick={downloadCSV} variant="hero">
              <Download className="mr-2 h-4 w-4" /> Download CSV
            </Button>
          </div>
          <div className="max-h-[480px] overflow-auto rounded-xl border border-border">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-secondary text-secondary-foreground">
                <tr>
                  <th className="px-3 py-2 text-left">#</th>
                  {FEATURES.map((f) => (
                    <th key={f} className="px-3 py-2 text-left font-semibold">{f}</th>
                  ))}
                  <th className="px-3 py-2 text-left">Risk %</th>
                  <th className="px-3 py-2 text-left min-w-[88px]">Class</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} className="border-t border-border odd:bg-background/40">
                    <td className="px-3 py-2 text-muted-foreground">{i + 1}</td>
                    {FEATURES.map((f) => (
                      <td key={f} className="px-3 py-2 tabular-nums">{r[f]}</td>
                    ))}
                    <td className="px-3 py-2 font-semibold tabular-nums">
                      {r.__result ? (r.__result.probability * 100).toFixed(1) + "%" : "—"}
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className="inline-flex items-center justify-center rounded-full px-3 py-1.5 text-sm font-bold text-primary-foreground whitespace-nowrap min-w-[72px]"
                        style={{
                          background:
                            r.__result?.label === "HIGH RISK"
                              ? "hsl(var(--risk-high))"
                              : "hsl(var(--risk-low))",
                        }}
                      >
                        {r.__result?.label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
