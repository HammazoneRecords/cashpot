# PLAN: Cash Pot 6-Layer Engine + Strategy Dashboard + Accuracy Tracker

**Created:** 2026-07-03
**Status:** ✅ COMPLETED

## Summary
Expanded from 4→6 layers (Time Series + Astro), built 2-day forecast engine, added Strategy Dashboard tab where each strategy is its own card showing raw output + streak + trending. Accuracy tracking wired into UI. Sauce stays hidden — users see per-strategy outputs but not how engine weights/combines.

## What Got Built

### Python Engine (`predictor.py`)
- Fixed duplicate `score()` function bug (modifier was dead code)
- Wired `--dream=` and `--strategy=` CLI flags into JSON command
- Momentum F-01 wired into scoring (was `pass` stub)
- **Layer 5: TimeSeriesAnalysis** — S31 MultiStep Trend, S33 SlotTrend, S34 DayPattern
- **Layer 6: AstroAnalysis** — S35 MoonPhase (pure math, no API), S36 PlanetaryRuler, S37 PlanetaryHour, S38 VoidOfCourse
- **`strategies` command** — 22 strategies outputting raw JSON for dashboard
- **`forecast` command** — N-step ahead with confidence decay
- **`accuracy` command** — hit rate breakdown by strategy/slot
- **`moon` command** — current moon phase + planetary ruler

### Server (`server.ts`)
- `GET /api/strategies` — strategy dashboard data
- `GET /api/forecast?days=2` — 12 draws ahead
- `GET /api/accuracy` — hit rate stats
- `GET /api/moon` — astro context
- `POST /api/log-hit` — record correct predictions
- `POST /api/predict` enhanced — passes dream + strategy to Python, returns full ranking

### Frontend
- **Chart Tab** — Strategy Dashboard with 22 strategy cards, filterable by layer, expandable detail
- **AccuracyWidget** — hit rate ring + per-slot mini bars + log draw modal
- **ForecastView** — 2-day scrollable timeline with confidence bars
- 4 tabs: Engine | Dream | Results | Chart

## Files Created/Modified
| File | Action |
|------|--------|
| `python/predictor.py` | MODIFY — fixed bugs, 2 new classes, 4 new commands |
| `server.ts` | MODIFY — 6 new/updated endpoints |
| `src/types.ts` | MODIFY — 8 new interfaces |
| `src/App.tsx` | MODIFY — 4th tab, new components |
| `src/components/ChartView.tsx` | CREATE |
| `src/components/AccuracyWidget.tsx` | CREATE |
| `src/components/ForecastView.tsx` | CREATE |
| `src/index.css` | MODIFY — strategy card styles, filter chips, etc. |
