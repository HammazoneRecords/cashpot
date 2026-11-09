import { useState, useEffect, useRef } from "react";
import { Search } from "lucide-react";
import { SYMBOLS } from "../data/symbols";

export default function DreamView() {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Autofocus on tab open
    inputRef.current?.focus();
  }, []);

  const matches = query.trim().length === 0 ? [] : SYMBOLS.filter(s =>
    s.keywords.some(k => k.includes(query.toLowerCase().trim())) ||
    s.name.toLowerCase().includes(query.toLowerCase().trim())
  );

  return (
    <div className="space-y-5">
      {/* Search */}
      <div className="glass p-4">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Type what you dreamt — money, dog, fire, water..."
            className="w-full bg-white/[0.03] border border-white/[0.08] rounded-lg pl-9 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
          />
        </div>
        {query.trim().length > 0 && (
          <p className="text-[10px] text-slate-600 mt-2 font-mono">
            {matches.length} match{matches.length !== 1 ? "es" : ""} for &ldquo;{query}&rdquo;
          </p>
        )}
      </div>

      {/* Empty state */}
      {query.trim().length === 0 && (
        <div className="text-center py-12 text-slate-600">
          <p className="text-sm font-mono">Describe your dream to find your numbers</p>
          <p className="text-xs mt-2 text-slate-700">Try: money · dog · fire · water · horse · bird · dead</p>
        </div>
      )}

      {/* Results */}
      {matches.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {matches.map(sym => {
            const matched = sym.keywords.filter(k =>
              k.includes(query.toLowerCase().trim())
            );
            return (
              <div key={sym.number} className="glass p-4 flex items-start gap-4">
                <div className="ball-main shrink-0" style={{ width: 52, height: 52, fontSize: "1.25rem" }}>
                  {sym.number}
                </div>
                <div className="min-w-0">
                  <p className="font-bold text-slate-200 text-sm">{sym.name}</p>
                  {matched.length > 0 && (
                    <p className="text-[10px] text-indigo-400 font-mono mt-0.5">
                      matched: {matched.slice(0, 3).join(", ")}
                    </p>
                  )}
                  <p className="text-[10px] text-slate-600 mt-1 leading-relaxed">
                    {sym.keywords.slice(0, 4).join(" · ")}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {query.trim().length > 0 && matches.length === 0 && (
        <p className="text-center text-xs text-slate-600 font-mono py-8">
          No matches for &ldquo;{query}&rdquo;
        </p>
      )}
    </div>
  );
}
