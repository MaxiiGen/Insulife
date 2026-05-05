import { useState } from "react";
import { SinglePatientForm } from "@/components/SinglePatientForm";
import { BulkUpload } from "@/components/BulkUpload";
import succulent from "@/assets/succulent.png";
import { User, Users, Activity } from "lucide-react";

type Mode = "single" | "bulk";

const Index = () => {
  const [mode, setMode] = useState<Mode>("single");

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <header className="relative overflow-hidden rounded-b-[3rem] bg-[image:var(--gradient-hero)] px-6 pb-20 pt-10 text-primary-foreground md:px-12">
        <div className="absolute inset-0 bg-[image:var(--gradient-leaf)] opacity-70" />
        <nav className="relative z-10 mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-2 font-display text-xl font-bold lowercase tracking-wide">
            <Activity className="h-5 w-5" /> diabeta
          </div>
          <div className="text-xs uppercase tracking-[0.3em] opacity-70">XGBoost · ONNX</div>
        </nav>

        <div className="relative z-10 mx-auto mt-12 grid max-w-6xl items-center gap-10 md:grid-cols-2">
          <div>
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.3em] opacity-80">
              Clinical decision support
            </p>
            <h1 className="font-display text-6xl font-bold leading-[0.95] md:text-8xl">
              Diabetes<br />risk, in<br />seconds.
            </h1>
            <p className="mt-6 max-w-md text-base opacity-80">
              A trained XGBoost model classifies patient risk from eight clinical features.
              Score one patient or a whole cohort.
            </p>
          </div>
          <div className="relative flex justify-center md:justify-end">
            <img
              src={succulent}
              alt="Botanical illustration"
              width={420}
              height={420}
              className="drop-shadow-2xl"
            />
          </div>
        </div>
      </header>

      <main className="mx-auto -mt-12 max-w-6xl px-6 pb-20 md:px-12">
        {/* Mode toggle - mimics image's tab style */}
        <div className="mb-8 flex items-center gap-3">
          <ModeChip
            active={mode === "single"}
            onClick={() => setMode("single")}
            icon={<User className="h-4 w-4" />}
            label="Single patient"
            badge="1"
          />
          <ModeChip
            active={mode === "bulk"}
            onClick={() => setMode("bulk")}
            icon={<Users className="h-4 w-4" />}
            label="Bulk upload"
            badge="CSV"
          />
        </div>

        {mode === "single" ? <SinglePatientForm /> : <BulkUpload />}

        <footer className="mt-16 border-t border-border pt-6 text-center text-xs text-muted-foreground">
          For research and educational use only. Not a substitute for medical diagnosis.
        </footer>
      </main>
    </div>
  );
};

const ModeChip = ({
  active, onClick, icon, label, badge,
}: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string; badge: string }) => (
  <button
    onClick={onClick}
    className={`group flex items-center gap-3 rounded-full px-5 py-3 font-display text-lg transition-all ${
      active
        ? "bg-primary text-primary-foreground shadow-[var(--shadow-card)]"
        : "bg-card text-muted-foreground hover:text-foreground"
    }`}
  >
    <span
      className={`flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 text-[10px] font-bold ${
        active ? "bg-primary-foreground text-primary" : "bg-secondary text-secondary-foreground"
      }`}
    >
      {badge}
    </span>
    {icon}
    <span>{label}</span>
  </button>
);

export default Index;
