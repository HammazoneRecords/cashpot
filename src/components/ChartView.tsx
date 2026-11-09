import { useState, useEffect } from "react";
import type { StrategyDashboard, LayerName } from "../types";
import { SYMBOLS } from "../data/symbols";

const LAYER_COLORS: Record<LayerName, string> = {
  math: "#6366f1", domain: "#22c55e", superstition: "#f97316",
  root: "#a855f7", timeseries: "#14b8a6", astro: "#eab308",
};

const LAYER_LABELS: Record<LayerName, string> = {
  math: "Math", domain: "Domain", superstition: "Superstition",
  root: "Root", timeseries: "Time", astro: "Astro",
};

const FILTERS: Array<LayerName | "all"> = ["all", "math", "domain", "superstition", "root", "timeseries", "astro"];

const symName = (n: number) => SYMBOLS.find(s => s.number === n)?.name ?? `#${n}`;
const symEmoji = (n: number) => SYMBOLS.find(s => s.number === n)?.emoji ?? "";

export default function ChartView() {
  const [data, setData] = useState<StrategyDashboard | null>(null);
  const [filter, setFilter] = useState<LayerName | "all">("all");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/strategies")
      .then(r => r.ok ? r.json() : null)
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center text-xs text-slate-500 font-mono py-12">Loading strategies...</div>;
  if (!data || !data.strategies.length) return <div className="text-center text-xs text-slate-600 font-mono py-12">No strategies available. Run a prediction first.</div>;

  const filtered = filter === "all"
    ? data.strategies
    : data.strategies.filter(s => s.layer === filter);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">Strategy Dashboard</p>
          <p className="text-indigo-300 font-bold text-sm">Target: {data.targetDow}</p>
        </div>
        <div className="flex gap-1 flex-wrap">
          {FILTERS.map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`filter-chip ${filter === f ? "active" : ""}`}
              style={f !== "all" ? { borderColor: LAYER_COLORS[f as LayerName], color: filter === f ? LAYER_COLORS[f as LayerName] : undefined } : {}}
            >
              {f === "all" ? "All" : LAYER_LABELS[f as LayerName]}
            </button>
          ))}
        </div>
      </div>

      {/* Strategy cards — 6-column grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {filtered.map(card => (
          <div key={card.id} className={`strategy-card ${card.streak.status}`}
            onClick={() => setExpanded(expanded === card.id ? null : card.id)}>
            {/* Card header — compact */}
            <div className="flex items-center gap-1.5 px-2 py-1.5 cursor-pointer">
              <span className="text-sm shrink-0">{card.glyph}</span>
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-bold text-slate-300 leading-tight">{card.id}</p>
                <p className="text-[9px] text-slate-500 font-mono leading-tight">{LAYER_LABELS[card.layer]}</p>
              </div>
              <span className={`streak-dot ${card.streak.status} shrink-0`} />
            </div>

            {/* Card body — ultra compact */}
            <div className="px-2 pb-2">
              {card.output.type === "ranked_numbers" && card.output.numbers && (
                <div className="flex flex-wrap gap-1">
                  {(expanded === card.id ? card.output.numbers.slice(0, 6) : card.output.topPicks || card.output.numbers.slice(0, 2))
                    .map(n => (
                      <span key={n} className="text-[9px] bg-white/[0.04] rounded px-1 py-0.5">
                        {symEmoji(n)} <b className="text-indigo-300">{n}</b>
                      </span>
                    ))}
                </div>
              )}

              {card.output.type === "gap_range" && (
                <div className="space-y-1">
                  <div className="flex gap-1 flex-wrap">
                    <span className="text-[8px] text-amber-400 font-mono">Big:</span>
                    {card.output.biggestGaps?.map(n => (
                      <span key={n} className="text-[9px] bg-amber-400/[0.06] rounded px-1">{symEmoji(n)} <b className="text-amber-300">{n}</b></span>
                    ))}
                  </div>
                  <div className="flex gap-1 flex-wrap">
                    <span className="text-[8px] text-green-400 font-mono">Rec:</span>
                    {card.output.smallestGaps?.map(n => (
                      <span key={n} className="text-[9px] bg-green-400/[0.06] rounded px-1">{symEmoji(n)} <b className="text-green-300">{n}</b></span>
                    ))}
                  </div>
                </div>
              )}

              {card.output.type === "range_pick" && (
                <div>
                  <span className="text-[8px] text-indigo-400 font-mono uppercase">{card.output.recommendedRange}</span>
                  {card.output.distribution && (
                    <div className="flex gap-1 mt-0.5">
                      <div className="flex-1 h-1 rounded-sm bg-indigo-500/40" style={{width:`${(card.output.distribution.low||0)/30*100}%`}} />
                      <div className="flex-1 h-1 rounded-sm bg-amber-500/40" style={{width:`${(card.output.distribution.mid||0)/30*100}%`}} />
                      <div className="flex-1 h-1 rounded-sm bg-red-500/40" style={{width:`${(card.output.distribution.high||0)/30*100}%`}} />
                    </div>
                  )}
                </div>
              )}

              {card.output.type === "followers" && (
                <div className="flex gap-1 flex-wrap">
                  <span className="text-[8px] text-slate-500 font-mono">→</span>
                  {card.output.followers?.map((n, i) => (
                    <span key={n} className="text-[9px] bg-white/[0.04] rounded px-1">
                      {symEmoji(n)} <b className="text-indigo-300">{n}</b><span className="text-slate-600">({card.output.counts?.[i]}x)</span>
                    </span>
                  ))}
                </div>
              )}

              {card.output.currentPhase && (
                <p className="text-[10px] text-slate-500 font-mono">Phase: {card.output.currentPhase}</p>
              )}
            </div>

            {/* Expanded detail */}
            {expanded === card.id && card.output.numbers && card.output.numbers.length > 3 && (
              <div className="px-4 pb-3 pt-0 border-t border-white/[0.06] mx-4 mt-1">
                <p className="text-[10px] text-slate-600 font-mono mt-2 mb-1">All ranked ({card.output.numbers.length} numbers)</p>
                <div className="flex flex-wrap gap-1.5">
                  {card.output.numbers.map((n, i) => (
                    <span key={n} className="text-[9px] text-slate-500 font-mono">
                      {i + 1}.{symName(n)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Compass legend */}
      <div className="glass p-4">
        <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-3">Compass Layers</p>
        <div className="flex flex-wrap gap-3">
          {(["math","domain","superstition","root","timeseries","astro"] as LayerName[]).map(l => (
            <div key={l} className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: LAYER_COLORS[l] }} />
              <span className="text-[10px] text-slate-400 font-mono">{LAYER_LABELS[l]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
