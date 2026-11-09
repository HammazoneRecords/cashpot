# Cash Pot Engine — Next Steps
**Last updated:** 2026-06-24

---

## Done
- [x] Clean stack — Vite + React + TS + Express + pnpm (no Gemini, no AI Studio artifacts)
- [x] Python predictor.py wired via child_process (deterministic, 36-number ranking)
- [x] `/api/predict` — returns top 3 picks + reversal (bottom 3) + DeepSeek analysis note
- [x] `/api/recent-draws` — serves last 120 draws from cash_pot_results.json
- [x] Engine view — auto-fires on load, draw slot pills, strategy pills, dream input
- [x] Reversal row — lowest-confidence picks displayed below main picks
- [x] Dream Decoder — instant as-you-type local symbol lookup
- [x] Results Board — add draws, scrollable history
- [x] Minimal glassmorphism dark indigo UI

---

## Next — Before Launch

### P0 (Blocking)
- [ ] **Browser test** — confirm Engine view renders and auto-trigger fires on load
- [ ] **Predictor.py `json` command** — verify `predictor.py json 36 --dow=<day>` outputs correct JSON with `{predictions:[{number,name,score}]}` format. If not, add the json output flag.
- [ ] **Update draw data** — `python/cash_pot_results.json` is June 1–21, 2026. Refresh with current draws before launch.

### P1 (Should ship with)
- [ ] **GitHub repo** — create `HammazoneRecords/cashpot`, push, set main as default
- [ ] **Dockerfile** — pnpm + python3 in runner stage (see plan)
- [ ] **VPS deploy** — docker-compose service at port 4002, nginx conf for `cashpot.mindwaveja.com`
- [ ] **APPS.md entry** — add cashpot row to `vps_management/APPS.md`
- [ ] **SSL cert** — certbot for cashpot.mindwaveja.com
- [ ] **BRANCH_STATUS.md** — create from template

### P2 (Post-launch)
- [ ] **Live draw data feed** — auto-update cash_pot_results.json daily (scrape or manual entry via Results Board)
- [ ] **Admin: bulk add draws** — paste CSV or multi-draw entry form
- [ ] **Prediction accuracy tracker** — after each draw, mark if engine was right. Build hit-rate stat over time.
- [ ] **Umami analytics** — add tracking script once deployed
- [ ] **PWA manifest** — installable on mobile (most users are phone-first)

---

## Known Gaps
- `raw.ts` in `src/data/` is a leftover from the build — delete it
- `cashpot-aistudio-archive/` still in `active_apps/` — move to vault when confirmed done
- predictor.py currently uses relative imports inside `python/` folder — confirm it runs standalone with `cwd=python/`
