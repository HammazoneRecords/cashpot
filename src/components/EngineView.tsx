import { useState, useEffect, useRef } from "react";
import { RefreshCw } from "lucide-react";
import type { Draw, PredictionResult, Strategy } from "../types";
import { SYMBOLS } from "../data/symbols";

// Jamaican draw schedule (UTC-5)
const DRAW_SLOTS = [
  { label: "Early Bird", h: 8,  m: 30 },
  { label: "Morning",    h: 10, m: 30 },
  { label: "Midday",     h: 13, m: 0  },
  { label: "Mid-Afternoon", h: 15, m: 0 },
  { label: "Drivetime", h: 17, m: 0  },
  { label: "Evening",   h: 20, m: 25 },
];

function getNextSlot(): string {
  const nowUtc = Date.now();
  const jmDate = new Date(nowUtc - 5 * 60 * 60 * 1000);
  const h = jmDate.getUTCHours(), m = jmDate.getUTCMinutes();
  const next = DRAW_SLOTS.find(s => s.h > h || (s.h === h && s.m > m));
  return next?.label ?? "Early Bird";
}

interface Props { draws: Draw[]; }

export default function EngineView({ draws }: Props) {
  const [drawTime, setDrawTime] = useState(getNextSlot);
  const [strategy, setStrategy] = useState<Strategy>("hybrid");
  const [dreamText, setDreamText] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const firedRef = useRef(false);
  const dreamTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  async function predict(dt = drawTime, st = strategy, dream = dreamText) {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ drawTime: dt, strategy: st, dreamText: dream }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError("Engine unavailable. Check server.");
    } finally {
      setLoading(false);
    }
  }

  // Auto-fire once draws are loaded
  useEffect(() => {
    if (draws.length > 0 && !firedRef.current) {
      firedRef.current = true;
      predict();
    }
  }, [draws]);

  // Strategy change → re-predict
  function handleStrategy(s: Strategy) {
    setStrategy(s);
    if (firedRef.current) predict(drawTime, s, dreamText);
  }

  // Draw time change → re-predict
  function handleDrawTime(dt: string) {
    setDrawTime(dt);
    if (firedRef.current) predict(dt, strategy, dreamText);
  }

  // Dream input → debounced re-predict
  function handleDream(val: string) {
    setDreamText(val);
    if (dreamTimer.current) clearTimeout(dreamTimer.current);
    dreamTimer.current = setTimeout(() => {
      if (firedRef.current) predict(drawTime, strategy, val);
    }, 600);
  }

  const symFor = (n: number) => SYMBOLS.find(s => s.number === n);

  return (
    <div className="space-y-5">

      {/* Controls row */}
      <div className="glass p-4 space-y-4">
        {/* Draw slot pills */}
        <div>
          <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-2">Draw Slot</p>
          <div className="flex flex-wrap gap-1.5">
            {DRAW_SLOTS.map(s => (
              <button
                key={s.label}
                onClick={() => handleDrawTime(s.label)}
                className={`strategy-pill ${drawTime === s.label ? "active" : ""}`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Strategy + dream row */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div>
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-2">Strategy</p>
            <div className="flex gap-1.5">
              {(["math","hybrid","dream"] as Strategy[]).map(s => (
                <button
                  key={s}
                  onClick={() => handleStrategy(s)}
                  className={`strategy-pill ${strategy === s ? "active" : ""}`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1">
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-2">Dream (optional)</p>
            <input
              type="text"
              value={dreamText}
              onChange={e => handleDream(e.target.value)}
              placeholder="Describe what you dreamt..."
              className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Result card */}
      <div className="glass p-6">
        {/* Card header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">Next draw</p>
            <p className="text-indigo-300 font-bold text-sm mt-0.5">{drawTime}</p>
          </div>
          <button
            onClick={() => predict()}
            disabled={loading}
            className="p-2 rounded-lg hover:bg-white/[0.06] text-slate-500 hover:text-slate-300 transition-all disabled:opacity-40"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

        {loading && !result && (
          <div className="py-10 flex items-center justify-center gap-3 text-slate-500">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span className="text-xs font-mono">Running engine...</span>
          </div>
        )}

        {error && (
          <p className="text-xs text-red-400 text-center py-4">{error}</p>
        )}

        {result && (
          <div className="space-y-6">
            {/* Main picks */}
            <div>
              <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-4 text-center">Engine picks</p>
              <div className="flex justify-center gap-8">
                {result.numbers.map((n, i) => {
                  const sym = symFor(n);
                  return (
                    <div key={n} className="flex flex-col items-center gap-2">
                      <div className={`ball-main ${loading ? "opacity-50" : ""}`}>{n}</div>
                      <p className="text-[10px] text-slate-400 font-mono font-bold uppercase tracking-wide text-center leading-tight">
                        {sym?.name ?? result.names[i]}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Reversal */}
            <div className="border-t border-white/[0.06] pt-5">
              <p className="text-[10px] text-slate-600 font-mono uppercase tracking-widest mb-3 text-center">
                Reversal — lowest confidence
              </p>
              <div className="flex justify-center gap-5">
                {result.reversal.map((n, i) => {
                  const sym = symFor(n);
                  return (
                    <div key={n} className="flex flex-col items-center gap-1.5">
                      <div className={`ball-reversal ${loading ? "opacity-40" : ""}`}>{n}</div>
                      <p className="text-[9px] text-slate-600 font-mono uppercase text-center leading-tight">
                        {sym?.name ?? result.reversalNames[i]}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Analysis */}
            {result.analysis && (
              <div className="border-t border-white/[0.06] pt-4">
                <p className="text-[11px] text-slate-400 leading-relaxed italic">
                  {result.analysis}
                </p>
              </div>
            )}

            {result.fallback && (
              <p className="text-[9px] text-amber-600 font-mono text-center">
                fallback — python engine unavailable
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
