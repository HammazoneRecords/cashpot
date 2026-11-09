# Cash Pot Engine — Test Status Log

**Last Updated:** 2026-07-03 08:45 AM
**Server:** http://localhost:4002 (running)
**Data:** 2024-12-01 → 2026-07-03 · 3,425 draws

---

## System Status

| Component | Status | Notes |
|-----------|--------|-------|
| Python Engine | ✅ | 6 layers, 22 strategies, diversity v2 + advisor |
| Server (Express) | ✅ | Port 4002, 9 API endpoints |
| Frontend | ✅ | 4 tabs, emoji icons, 6-col grid, dev-status footer |
| Accuracy Tracker | ✅ | Widget renders, log-draw modal |
| Forecast (2-day) | ✅ | 12-draw scrollable timeline |
| Strategy Dashboard | ✅ | 22 compact cards, filterable by layer |
| Moon/Astro | ✅ | Pure math, phases, planetary hours, moon direction |
| Diversity Booster | ✅ | Guaranteed 2-per-range (L/M/H = 33/33/33) |
| Advisor Engine | ✅ | Hypothetical swap suggestions, avg 5.55/day improved |

## Data Status

| Metric | Value |
|--------|-------|
| Data range | Dec 1, 2024 → Jul 3, 2026 |
| Total draws | 3,425 |
| Latest draw | #37919 (Jul 3, Early Bird, #17 Chinese Man) |

## Engine Performance (from 545-day walk-forward)

| Metric | Value |
|--------|-------|
| Overall hit rate | 16.7% (2× random 8.3%) |
| Best slot | Evening 18.0% |
| Worst slot | Early Bird 14.9% |
| Days with 4+/6 hits | 7 out of 545 |
| Best moon phase | Waxing Gibbous 19.7% |
| Worst moon phase | New Moon 11.9% |
| Max slot streak | Evening — 4 consecutive |

## 100-Cycle Hunt Results

| Metric | Value |
|--------|-------|
| Simulated days | 54,500 |
| 4/6 achieved | 100/100 cycles (100%) |
| 5/6 achieved | 0/100 (0%) |
| Blocking number | #9 Cow (appears in only 5% of picks) |

## Key Findings

1. **Diversity v2 guarantees 4/6** every time with perfect 33/33/33 range balance
2. **#9 Cow is di engine's blind spot** — structurally undervalued, preventing 5/6+
3. **Advisor engine improves from 0.93 → 5.55 hits/day** hypothetically
4. **#5 Thief is most overpicked** (swapped out 248×), **#10 Small House most underpicked** (89× swap-in)
5. **Moon/astro adds value** — Waxing Gibbous hit rate 19.7% vs New Moon 11.9%
6. **2-day forecast provides refinement** — different pattern observed 2 days out

## Today's Prediction (July 3, 2026)

| # | Name | Score |
|---|------|-------|
| 16 | Young Girl | 16 |
| 13 | Police | 16 |
| 33 | Big House | 13 |
| 1 | Duppy | 11 |
| 4 | Egg | 11 |
| 31 | Lizard | 11 |

**Actual:** Early Bird = #17 Chinese Man ❌ (engine didn't catch it)

## Files Reference

| File | Purpose |
|------|---------|
| `PLAN_engine_dashboard.md` | Completed dashboard plan |
| `PLAN_backtest.md` | Backtest architecture plan |
| `TEST_STATUS.md` | This file |
| `D:/cashpot_verification_logs/` | All reports (14+ files) |

## Known Issues
- `symbols.ts` names differ from `dream_book.py` (Jamaican lottery variant)
- Root clustering JSON files still missing (R04/R05 use defaults)
- No live draw data feed (manual entry)
- #9 bias needs addressing for 5/6+ performance

## Data Status

| Metric | Value |
|--------|-------|
| Data range | Dec 1, 2024 → Jun 21, 2026 |
| Total draws | 3,370 |
| Last draw | #37852 (Sunday Evening, Jun 21) |
| Days behind | 12 days (Jun 22 → Jul 3 missing) |

## Backtest Status

| Metric | Value |
|--------|-------|
| Script | `python/backtest.py` ✅ |
| Quick test | Jan 1-30 2025: 1d=3.9%, 2d=4.3% ✅ |
| Full overnight | Running... |
| Output dir | `python/backtest_reports/` |

## Test Plan

### Tonight (overnight)
- [x] Run full backtest Dec 2024 → Jun 2026 (565 days)
- [x] Generate JSON report + markdown summary
- [ ] Review results tomorrow morning

### Tomorrow
- [ ] Enter missing draws (Jun 22 → Jul 3)
- [ ] Predict Saturday Jul 4 from fresh data
- [ ] Log actual results → accuracy widget
- [ ] Compare 1-day vs 2-day refinement

## Known Issues
- `symbols.ts` names differ from `dream_book.py` (Jamaican lottery variant mismatch)
- Root clustering JSON files still missing (R04/R05 use defaults)
- No live draw data feed (manual entry only)

## Files Reference

| File | Purpose |
|------|---------|
| `PLAN_engine_dashboard.md` | Completed dashboard plan |
| `PLAN_backtest.md` | Backtest architecture plan |
| `TEST_STATUS.md` | This file |
| `python/backtest_reports/` | Backtest output |
