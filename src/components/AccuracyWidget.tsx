import { useState, useEffect } from "react";
import type { AccuracyStats } from "../types";

const SLOTS = ["Early Bird","Morning","Midday","Mid-Afternoon","Drivetime","Evening"];

export default function AccuracyWidget() {
  const [stats, setStats] = useState<AccuracyStats | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [logSlot, setLogSlot] = useState("Evening");
  const [logNum, setLogNum] = useState("");

  useEffect(() => {
    fetch("/api/accuracy")
      .then(r => r.ok ? r.json() : null)
      .then(d => setStats(d))
      .catch(() => {});
  }, []);

  const refresh = () => {
    fetch("/api/accuracy")
      .then(r => r.ok ? r.json() : null)
      .then(d => setStats(d))
      .catch(() => {});
  };

  const handleLog = async () => {
    const n = parseInt(logNum);
    if (!n || n < 1 || n > 36) return;
    await fetch("/api/log-hit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ draw: logSlot, number: n, predicted: [] }),
    });
    setLogNum("");
    setShowModal(false);
    setTimeout(refresh, 500);
  };

  const rate = stats?.hitRate ?? 0;
  const hits = stats?.totalHits ?? 0;
  const total = stats?.totalPredictions ?? 0;
  const circumference = 2 * Math.PI * 20;
  const offset = circumference - (rate / 100) * circumference;

  return (
    <div className="glass p-4">
      <div className="flex items-center justify-between mb-3">
        <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">Accuracy</p>
        <button onClick={() => setShowModal(true)} className="text-[9px] text-indigo-400 font-mono hover:text-indigo-300">+ Log Draw</button>
      </div>

      <div className="flex items-center gap-4">
        {/* Ring */}
        <div className="relative w-14 h-14 shrink-0">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 48 48">
            <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
            <circle cx="24" cy="24" r="20" fill="none" stroke="#6366f1" strokeWidth="4"
              strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-indigo-300">{rate}%</span>
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-xs text-slate-400 font-mono">{hits} / {total} hits</p>
          {/* Per-slot mini bars */}
          <div className="flex gap-1 mt-2">
            {SLOTS.map(s => {
              const slotRate = stats?.bySlot?.[s] ?? 0;
              return (
                <div key={s} className="flex-1 flex flex-col items-center" title={`${s}: ${slotRate}%`}>
                  <div className="w-full h-8 bg-white/[0.03] rounded-sm overflow-hidden">
                    <div className="w-full bg-indigo-500/40 rounded-sm"
                      style={{ height: `${Math.min(slotRate, 100)}%`, marginTop: "auto" }} />
                  </div>
                  <span className="text-[7px] text-slate-600 mt-1">{s.slice(0, 3)}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Log Draw Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.6)" }}
          onClick={() => setShowModal(false)}>
          <div className="glass p-6 w-64 space-y-3" onClick={e => e.stopPropagation()}>
            <p className="text-sm font-bold text-slate-200">Log Draw Result</p>
            <select value={logSlot} onChange={e => setLogSlot(e.target.value)}
              className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg px-3 py-2 text-xs text-slate-200">
              {SLOTS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <input type="number" min={1} max={36} value={logNum}
              onChange={e => setLogNum(e.target.value)} placeholder="Winning #"
              className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600"
              onKeyDown={e => e.key === "Enter" && handleLog()} />
            <div className="flex gap-2">
              <button onClick={() => setShowModal(false)}
                className="flex-1 py-1.5 rounded-lg text-[10px] font-mono text-slate-500 border border-white/[0.08]">Cancel</button>
              <button onClick={handleLog}
                className="flex-1 py-1.5 rounded-lg text-[10px] font-bold bg-indigo-600/80 text-white">Log</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
