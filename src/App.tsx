import { useState, useEffect } from "react";
import type { Draw, View } from "./types";
import EngineView from "./components/EngineView";
import DreamView from "./components/DreamView";
import ResultsView from "./components/ResultsView";
import ChartView from "./components/ChartView";
import AccuracyWidget from "./components/AccuracyWidget";
import ForecastView from "./components/ForecastView";

export default function App() {
  const [view, setView] = useState<View>("engine");
  const [draws, setDraws] = useState<Draw[]>([]);
  const [dataRange, setDataRange] = useState("");
  const [devStatus, setDevStatus] = useState<{ running: boolean; task?: string; progress?: string; updated?: string; best?: number; found_5of6?: boolean } | null>(null);

  useEffect(() => {
    // Load draws from server (reads cash_pot_results.json)
    fetch("/api/recent-draws")
      .then(r => r.ok ? r.json() : [])
      .then((data: Draw[]) => {
        setDraws(data);
        try { localStorage.setItem("cashpot_draws", JSON.stringify(data)); } catch {}
      })
      .catch(() => {
        try {
          const cached = localStorage.getItem("cashpot_draws");
          if (cached) setDraws(JSON.parse(cached));
        } catch {}
      });
    // Data range from health endpoint
    fetch("/api/health")
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.dataRange?.first) {
          setDataRange(`${d.dataRange.first} → ${d.dataRange.last} · ${d.dataRange.total} draws`);
        }
      })
      .catch(() => {});
  }, []);

  // Dev-status polling (every 5s)
  useEffect(() => {
    const poll = () => fetch("/api/dev-status")
      .then(r => r.ok ? r.json() : null)
      .then(d => setDevStatus(d))
      .catch(() => {});
    poll();
    const id = setInterval(poll, 5000);
    return () => clearInterval(id);
  }, []);

  const addDraw = (draw: Draw) => {
    const updated = [draw, ...draws].sort((a, b) => b.index - a.index);
    setDraws(updated);
    try { localStorage.setItem("cashpot_draws", JSON.stringify(updated)); } catch {}
  };

  return (
    <div className="min-h-screen" style={{ background: "#080B18" }}>
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/[0.06]"
        style={{ background: "rgba(8,11,24,0.9)", backdropFilter: "blur(12px)" }}>
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <span className="font-black text-white tracking-tight text-sm">
              CASH POT <span className="text-indigo-400">ENGINE</span>
            </span>
            <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mt-0.5">
              {dataRange || "Loading data..."}
            </p>
          </div>

          <nav className="flex items-center gap-1 bg-white/[0.03] rounded-full p-1 border border-white/[0.06]">
            {(["engine", "dream", "results", "chart"] as View[]).map(v => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`nav-pill ${view === v ? "active" : ""}`}
              >
                {v === "engine" ? "Engine" : v === "dream" ? "Dream" : v === "results" ? "Results" : "Chart"}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Body */}
      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {view === "engine" && (
          <>
            <AccuracyWidget />
            <EngineView draws={draws} />
          </>
        )}
        {view === "dream" && <DreamView />}
        {view === "results" && <ResultsView draws={draws} onAdd={addDraw} />}
        {view === "chart" && (
          <>
            <AccuracyWidget />
            <ChartView />
            <ForecastView />
          </>
        )}
      </main>

      {/* Dev-status footer */}
      {devStatus?.running && (
        <footer className="sticky bottom-0 z-50 border-t border-white/[0.06]"
          style={{ background: "rgba(8,11,24,0.95)", backdropFilter: "blur(12px)" }}>
          <div className="max-w-3xl mx-auto px-4 py-1.5 flex items-center gap-3 text-[10px] font-mono">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shrink-0" />
              <span className="text-green-400">{devStatus.task || "Running..."}</span>
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-500">{devStatus.progress}</span>
            {devStatus.best != null && (
              <>
                <span className="text-slate-600">|</span>
                <span className="text-amber-400">Best: {devStatus.best}/6</span>
              </>
            )}
            {devStatus.found_5of6 && (
              <span className="text-green-400 font-bold">5/6 FOUND!</span>
            )}
            <span className="ml-auto text-slate-700">{devStatus.updated || ""}</span>
          </div>
        </footer>
      )}

      {devStatus && !devStatus.running && devStatus.task && (
        <footer className="sticky bottom-0 z-50 border-t border-white/[0.06]"
          style={{ background: "rgba(8,11,24,0.95)", backdropFilter: "blur(12px)" }}>
          <div className="max-w-3xl mx-auto px-4 py-1.5 flex items-center gap-2 text-[10px] font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-600 shrink-0" />
            <span className="text-slate-500">{devStatus.task}</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-600">{devStatus.progress}</span>
            {devStatus.best != null && (
              <>
                <span className="text-slate-600">|</span>
                <span className="text-slate-600">Best: {devStatus.best}/6</span>
              </>
            )}
          </div>
        </footer>
      )}
    </div>
  );
}
