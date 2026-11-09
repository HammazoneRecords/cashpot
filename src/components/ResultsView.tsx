import { useState } from "react";
import { Plus } from "lucide-react";
import type { Draw } from "../types";
import { SYMBOLS } from "../data/symbols";

const SLOTS = ["Early Bird","Morning","Midday","Mid-Afternoon","Drivetime","Evening"];

interface Props {
  draws: Draw[];
  onAdd: (d: Draw) => void;
}

export default function ResultsView({ draws, onAdd }: Props) {
  const [slot, setSlot] = useState("Evening");
  const [num, setNum] = useState("");
  const [err, setErr] = useState("");

  function handleAdd() {
    const n = parseInt(num);
    if (!n || n < 1 || n > 36) { setErr("Enter a number 1–36"); return; }
    setErr("");
    const newDraw: Draw = {
      id: String(Date.now()),
      index: (draws[0]?.index ?? 0) + 1,
      drawTime: slot,
      winningNumber: n,
      date: new Date().toLocaleDateString("en-JM"),
    };
    onAdd(newDraw);
    setNum("");
  }

  const shown = draws.slice(0, 30);

  return (
    <div className="space-y-4">
      {/* Add draw */}
      <div className="glass p-4 flex flex-col sm:flex-row items-end gap-3">
        <div className="flex-1">
          <label className="text-[10px] text-slate-500 font-mono uppercase tracking-widest block mb-1.5">Draw Slot</label>
          <select
            value={slot}
            onChange={e => setSlot(e.target.value)}
            className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500/50"
          >
            {SLOTS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="w-24">
          <label className="text-[10px] text-slate-500 font-mono uppercase tracking-widest block mb-1.5">Number</label>
          <input
            type="number" min={1} max={36}
            value={num}
            onChange={e => setNum(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleAdd()}
            placeholder="1–36"
            className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
          />
        </div>
        <button
          onClick={handleAdd}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-bold transition-colors"
        >
          <Plus className="w-3.5 h-3.5" /> Add
        </button>
      </div>
      {err && <p className="text-xs text-red-400 font-mono px-1">{err}</p>}

      {/* Draw list */}
      <div className="glass overflow-hidden">
        {shown.length === 0 ? (
          <p className="text-center text-xs text-slate-600 font-mono py-8">No draws loaded</p>
        ) : (
          <div className="divide-y divide-white/[0.04]">
            {shown.map(d => {
              const sym = SYMBOLS.find(s => s.number === d.winningNumber);
              return (
                <div key={d.id} className="flex items-center gap-4 px-5 py-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-600/10 border border-indigo-500/20
                       flex items-center justify-center font-bold text-sm text-indigo-300 shrink-0">
                    {d.winningNumber}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-slate-300">{sym?.name ?? `#${d.winningNumber}`}</p>
                    <p className="text-[10px] text-slate-600 font-mono">{d.drawTime} {d.date ? `· ${d.date}` : ""}</p>
                  </div>
                  <span className="text-[9px] font-mono text-slate-700">#{d.index}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
