import { useState, useEffect } from "react";
import type { ForecastResult, ForecastStep } from "../types";
import { SYMBOLS } from "../data/symbols";

const SLOTS = ["Early Bird","Morning","Midday","Mid-Afternoon","Drivetime","Evening"];

export default function ForecastView() {
  const [data, setData] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchForecast = () => {
    setLoading(true);
    fetch("/api/forecast?days=2")
      .then(r => r.ok ? r.json() : null)
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchForecast(); }, []);

  if (loading) return <div className="text-center text-xs text-slate-500 font-mono py-6">Loading forecast...</div>;
  if (!data || !data.forecast.length) return <div className="text-center text-xs text-slate-600 font-mono py-6">No forecast data</div>;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">2-Day Forecast</p>
        <button onClick={fetchForecast} className="text-[9px] text-indigo-400 font-mono hover:text-indigo-300">Refine</button>
      </div>

      {/* Horizontal scroll of cards */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {data.forecast.map((step, i) => {
          const slotIdx = i % 6;
          const dayOffset = Math.floor(i / 6);
          const isFar = dayOffset >= 1;
          const sym = SYMBOLS.find(s => s.number === step.number);
          return (
            <div key={i} className={`forecast-card glass shrink-0 w-36 p-3 ${isFar ? "far" : ""}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[9px] text-slate-500 font-mono">{SLOTS[slotIdx]}</span>
                <span className="text-[8px] text-slate-600 font-mono">+{dayOffset}d</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="ball-main shrink-0" style={{ width: 44, height: 44, fontSize: "1rem" }}>
                  {step.number}
                </div>
                <p className="text-[9px] text-slate-400 font-mono text-center leading-tight">{sym?.name ?? step.name}</p>
              </div>
              <div className="mt-2">
                <div className="flex items-center justify-between text-[8px] font-mono mb-1">
                  <span className="text-slate-600">Confidence</span>
                  <span className={step.confidence > 60 ? "text-green-400" : step.confidence > 40 ? "text-amber-400" : "text-slate-500"}>
                    {step.confidence}%
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                  <div className="h-full rounded-full transition-all"
                    style={{
                      width: `${step.confidence}%`,
                      background: step.confidence > 60 ? "#22c55e" : step.confidence > 40 ? "#f59e0b" : "#64748b"
                    }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
