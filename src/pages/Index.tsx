import { useState } from "react";
import { SinglePatientForm } from "@/components/SinglePatientForm";
import { BulkUpload } from "@/components/BulkUpload";
import heroImage from "@/assets/glucose-monitor.png";
import { User, Users, Activity, ShieldCheck, Zap, Database } from "lucide-react";

type Mode = "single" | "bulk";

const Index = () => {
  const [mode, setMode] = useState<Mode>("single");

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <header className="relative overflow-hidden rounded-b-[3rem] bg-[image:var(--gradient-hero)] px-6 pb-28 pt-8 text-primary-foreground md:px-12 md:pt-10">
        {/* Decorative glow */}
        <div className="pointer-events-none absolute inset-0 bg-[image:var(--gradient-leaf)] opacity-70" />
        <div className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-primary-foreground/5 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-40 -left-20 h-96 w-96 rounded-full bg-primary-foreground/5 blur-3xl" />

        <nav className="relative z-10 mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-2.5 font-display text-2xl font-bold tracking-tight">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-foreground/10 backdrop-blur">
              <Activity className="h-4 w-4" />
            </span>
            Insulife
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-primary-foreground/20 bg-primary-foreground/5 px-4 py-1.5 text-[10px] font-semibold uppercase tracking-[0.3em] sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-cream" />
            XGBoost · ONNX
          </div>
        </nav>

        <div className="relative z-10 mx-auto mt-16 grid max-w-6xl items-center gap-10 md:mt-20 md:grid-cols-[1.1fr_1fr]">
          <div>
            <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-primary-foreground/20 bg-primary-foreground/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.3em]">
              <span className="h-1 w-1 rounded-full bg-cream" />
              Clinical decision support
            </p>
            <h1 className="font-display text-6xl font-bold leading-[0.92] md:text-8xl">
              Diabetes<br />risk, in<br />
              <span className="italic text-cream">seconds.</span>
            </h1>
            <p className="mt-7 max-w-md text-base leading-relaxed opacity-80">
              A trained XGBoost model classifies patient risk from eight clinical features.
              Score one patient or an entire cohort — instantly, in your browser.
            </p>

            <div className="mt-10 grid max-w-md grid-cols-3 gap-4">
              <Stat icon={<Zap className="h-3.5 w-3.5" />} value="<1s" label="Inference" />
              <Stat icon={<ShieldCheck className="h-3.5 w-3.5" />} value="100%" label="On-device" />
              <Stat icon={<Database className="h-3.5 w-3.5" />} value="8" label="Features" />
            </div>
          </div>

          <div className="relative flex justify-center md:justify-end">
            <div className="absolute inset-0 m-auto h-72 w-72 rounded-full bg-cream/10 blur-2xl" />
            <img
              src={heroImage}
              alt="Glucose monitor device"
              width={460}
              height={460}
              className="relative drop-shadow-[0_25px_50px_rgba(0,0,0,0.4)]"
            />
          </div>
        </div>
      </header>

      <main className="mx-auto relative z-20 mt-12 max-w-6xl px-6 pb-20 md:px-12">
        <div className="mx-auto mb-8 flex items-center justify-center">
          <div className="inline-flex items-center gap-2.5 rounded-full border border-primary-foreground/20 bg-primary-foreground/5 p-1.5 shadow-[0_10px_30px_rgba(0,0,0,0.12)]">
            <ModeChip
              active={mode === "single"}
              onClick={() => setMode("single")}
              icon={<User className="h-4 w-4" />}
              label="Single patient"
            />
            <ModeChip
              active={mode === "bulk"}
              onClick={() => setMode("bulk")}
              icon={<Users className="h-4 w-4" />}
              label="Bulk CSV upload"
            />
          </div>
        </div>

        {mode === "single" ? <SinglePatientForm /> : <BulkUpload />}

        <footer className="mt-20 flex flex-col items-center gap-2 border-t border-border pt-8 text-center text-xs text-muted-foreground">
          <div className="flex items-center gap-2 font-display text-base text-foreground">
            <Activity className="h-3.5 w-3.5" /> Insulife
          </div>
          <p>For research and educational use only. Not a substitute for medical diagnosis.</p>
        </footer>
      </main>
    </div>
  );
};

const Stat = ({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) => (
  <div className="rounded-2xl border border-primary-foreground/15 bg-primary-foreground/5 p-3 backdrop-blur">
    <div className="flex items-center gap-1.5 text-cream/90">{icon}<span className="text-[9px] font-semibold uppercase tracking-wider">{label}</span></div>
    <div className="mt-1 font-display text-2xl font-bold">{value}</div>
  </div>
);

const ModeChip = ({
  active, onClick, icon, label,
}: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2.5 rounded-full px-5 py-2.5 text-sm font-semibold transition-all ${
      active
        ? "bg-primary text-primary-foreground shadow-[var(--shadow-card)]"
        : "text-muted-foreground hover:text-foreground"
    }`}
  >
    {icon}
    <span>{label}</span>
  </button>
);

export default Index;
