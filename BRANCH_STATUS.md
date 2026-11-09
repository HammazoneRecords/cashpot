# BRANCH_STATUS — cashpot

**App path:** `active_apps/cashpot/`
**Live domain:** `cashpot.mindwaveja.com` (not yet deployed)
**VPS container:** `mw-cashpot` (planned — port 4002)
**VPS port:** 4002
**Repo:** `HammazoneRecords/cashpot` (private, created 2026-11-06, main pushed)

---

## Current State

| Branch | Last Updated | Deployed? | Notes |
|---|---|---|---|
| main | 2026-11-06 | ⬜ Local only | On GitHub as of 2026-11-06 (commit `3bd1296`); not yet deployed to VPS |

## Last Action

**Date:** 2026-06-24
**Branch:** main (local)
**Action:** New app built from scratch
**What changed:**
- Clean Vite + React + TS + Express + pnpm scaffold
- Python predictor.py wired via child_process for deterministic predictions
- DeepSeek for factual analysis note only (not predictions)
- 3 views: Engine (auto-loads prediction), Dream Decoder (instant lookup), Results Board
- Reversal feature — bottom 3 of 36-number ranking displayed below main picks
- Glassmorphism dark indigo UI — minimal, no sensationalism
- NEXT_STEPS.md created with P0/P1/P2 checklist
**Schema migration:** none

---

## Active Feature Branches

None — all work on local main.

## Pending Merges

None yet — needs GitHub repo created first.

---

## History

| Date | Branch | Action | Notes |
|---|---|---|---|
| 2026-06-24 | main | App created — built from scratch | Replaces cashpot-aistudio-archive/ |
| 2026-06-23 | — | AI Studio version archived to cashpot-aistudio-archive/ | Original had Gemini, broken auto-trigger |
