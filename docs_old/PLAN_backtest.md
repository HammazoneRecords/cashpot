# PLAN: Cash Pot Backtesting Engine + Overnight Full Run

**Created:** 2026-07-03
**Status:** ⬜ IN PROGRESS

---

## Goal

Walk-forward backtest engine that simulates "live" prediction across the entire dataset. At each day, the engine sees ONLY data up to that day, predicts tomorrow AND 2-days-out, then reveals the actual results and scores everything. Runs from first available data point through last record — generates a comprehensive report measuring hit rates, reversal effectiveness, per-strategy accuracy, and 1-day vs 2-day refinement gains.

---

## Phase 1: Backtest Script (`python/backtest.py`)

### Architecture

```
walk_forward(records, start_at_draw=100, lookback=all)
  │
  ├─ For each day in range:
  │   ├─ visible = records up to current day ONLY
  │   ├─ Engine = PredictionEngine(visible)
  │   ├─ 1day_preds = Engine.predict(6, dow=next_day_dow)
  │   ├─ 2day_preds = Engine.predict(6, dow=day_after_dow)
  │   ├─ reveal ACTUAL results for next day (6 slots)
  │   ├─ For each of the 6 slots:
  │   │   ├─ hit_1d = winner in 1day top 3?
  │   │   ├─ hit_2d = winner in 2day top 3?
  │   │   ├─ reversal_hit = winner in reversal (bottom 3)?
  │   │   ├─ mirror_hit = 37-winner in top 3?
  │   │   ├─ root_match = winner root == any pick root?
  │   │   ├─ element_match = winner element == any pick element?
  │   │   ├─ range_match = winner in same low/mid/high as best pick?
  │   │   ├─ astro_match = winner planet == day ruler?
  │   │   └─ ghost = winner score == 0?
  │   └─ Per-strategy: test EACH strategy ALONE against each slot
  └─ Return JSON report
```

### Report Structure

```json
{
  "config": {
    "start_date": "2024-12-01",
    "end_date": "2026-06-21",
    "total_days_tested": 565,
    "total_slots_tested": 3390,
    "lookback_per_day": "all_available"
  },
  "engine_combined": {
    "one_day": {
      "hits": 0, "total": 3390, "hit_rate": 0,
      "by_slot": { "Early Bird": {"hits": 0, "total": 0, "rate": 0}, ... }
    },
    "two_day": {
      "hits": 0, "total": 3390, "hit_rate": 0,
      "refinement_gain": 0
    },
    "reversal": {
      "hits": 0, "total": 3390, "hit_rate": 0
    },
    "mirror": {
      "hits": 0, "total": 3390, "hit_rate": 0
    },
    "root_match": { "hits": 0, "rate": 0 },
    "element_match": { "hits": 0, "rate": 0 },
    "range_match": { "hits": 0, "rate": 0 },
    "astro_match": { "hits": 0, "rate": 0 },
    "ghost": { "count": 0, "rate": 0 }
  },
  "per_strategy": {
    "S01-Freq": { "hits": 0, "total": 3390, "hit_rate": 0, "by_slot": {...} },
    "S07-Gap": { ... },
    ...all 22 strategies...
  },
  "per_strategy_standalone": {
    "S01-Freq": {
      "hits": 0, "total": 3390, "hit_rate": 0,
      "reversal_hits": 0, "root_matches": 0, "element_matches": 0
    },
    ...
  },
  "day_by_day": [
    {
      "date": "2024-12-02",
      "dow": "Monday",
      "slots": [
        {
          "slot": "Early Bird",
          "winner": 14,
          "1d_top3": [7, 23, 15],
          "1d_hit": false,
          "2d_top3": [7, 23, 1],
          "2d_hit": false,
          "reversal_hit": true,
          "root_match": true,
          "element_match": false,
          "ghost": false
        },
        ...
      ]
    },
    ...
  ]
}
```

### Key Metrics Collected

| # | Metric | Description |
|---|--------|-------------|
| 1 | 1-day hits | Engine top 3 contains winner |
| 2 | 2-day hits | 2-day forecast top 3 contains winner |
| 3 | Refinement gain | 2-day caught it, 1-day missed |
| 4 | Reversal hits | Winner was in reversal bottom 3 |
| 5 | Mirror hits | 37-winner was in top 3 |
| 6 | Root matches | Winner root matches a pick root |
| 7 | Element matches | Winner element matches a pick element |
| 8 | Range matches | Winner in same low/mid/high range |
| 9 | Astro matches | Winner planet matches day ruler |
| 10 | Ghosts | Winner not ranked at all (score=0) |
| 11 | Per-strategy raw hits | Each strategy tested standalone |
| 12 | Per-slot breakdown | All metrics × 6 draw slots |

---

## Phase 2: CLI Integration

### New Command: `predictor.py backtest`

```
predictor.py backtest --start=2024-12-01 --end=2026-06-21 --output=backtest_report.json
```

Flags:
- `--start=` — start date (default: first date in data)
- `--end=` — end date (default: last date in data)
- `--output=` — output JSON filename (default: `backtest_report.json`)
- `--summary-only` — skip day-by-day, only output aggregate stats
- `--skip-strategies` — skip per-strategy standalone testing (faster)
- `--lookback=` — max draws to use for each prediction (default: all available)
- `--sliding` — use fixed sliding window (e.g., last 500 draws) instead of all available

### Output Files
- `python/backtest_report.json` — full data (day-by-day + aggregates)
- `python/backtest_summary.md` — human-readable summary
- `python/backtest_reports/` — directory fi future reports

---

## Phase 3: Run & Report

### Overnight Run
```
python backtest.py --start=2024-12-01 --end=2026-06-21
```

Generates:
1. `python/backtest_reports/2026-07-03_full.json` — complete data
2. `python/backtest_reports/2026-07-03_summary.md` — markdown summary

### Summary Table Template

```
# Backtest Report: Dec 2024 – Jun 2026

## Combined Engine
| Metric | Hits | Total | Rate |
|--------|------|-------|------|
| 1-Day Top 3 | X | 3390 | X% |
| 2-Day Top 3 | X | 3390 | X% |
| Reversal (fade) | X | 3390 | X% |
| Root Match | X | 3390 | X% |
| Element Match | X | 3390 | X% |
| Ghost (unranked) | X | 3390 | X% |

## Per Slot (1-Day)
| Slot | Hits | Rate |
|------|------|------|
| Early Bird | X | X% |
| Morning | X | X% |
| Midday | X | X% |
| Mid-Afternoon | X | X% |
| Drivetime | X | X% |
| Evening | X | X% |

## Top 5 Strategies (Standalone)
| Strategy | Hits | Rate |
|----------|------|------|
| S07-Gap | X | X% |
| S01-Freq | X | X% |
| ... | ... | ... |

## Key Findings
- Best slot: _____ 
- Ghost rate: _____ (engine blind spots)
- Reversal as strategy: _____ (fade the engine works X% of time)
- Short term vs long term: _____
```

---

## Files

| File | Action |
|------|--------|
| `python/backtest.py` | CREATE — full walk-forward engine |
| `python/predictor.py` | MODIFY — add `backtest` CLI command |
| `PLAN_backtest.md` | CREATE — this plan (in repo) |
| `python/backtest_reports/` | CREATE — directory for reports |

---

## Decisions
- Walk-forward approach: engine only sees data UP TO the prediction date
- 100-draw warmup before first prediction (need enough data for strategies)
- Tests all 6 layers combined AND each layer/strategy standalone
- Reports both aggregate stats AND day-by-day breakdown
- Runs overnight — full 565-day simulation ~15-30 min on decent machine
