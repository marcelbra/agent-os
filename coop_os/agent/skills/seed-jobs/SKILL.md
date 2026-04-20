---
description: Bootstrap or reset the job-search candidate pool with a broad multi-axis research sweep. Use once at the start, and again every ~quarter when the pool feels stale. Targets 30–50 net-new European AI-native Series A–C companies in a single session.
name: seed-jobs
---

## Purpose

The big bang. Rebuild the candidate pool from scratch (or refresh it wholesale). Runs across 4–5 research axes back-to-back and surfaces a large batch of matches. Budget ~2 hours.

For recurring daily top-ups, use `/scan-jobs` instead. For a read-only pipeline view, use `/track-jobs`.

## Required reading before running

- `coop_os/user/context/context-5-Job search profile & pool.md` — profile filter, existing pool (acts as exclusion list), and process convention. **Load this first.**
- `coop_os/workspace/milestones/milestone-9-Switch jobs — target 130-140k gross.md` — the milestone this work feeds.
- `coop_os/workspace/tasks/task-5-Job search research/description.md` — rolling research plan; its "Queued sources" section tells you which axes to prioritize.

## Steps

1. **Load context**
   - Read `context-5` (profile + pool + convention).
   - Read `task-5` (queued sources, last sweep date, market notes).
   - List existing `<Company> process` tasks under `milestone-9`.

2. **Frame the session with the user**
   - Confirm: "This is a ~2 hour session across 4–5 axes, targeting 30–50 new candidates. Good to go?"
   - Pick axes together — default selection:

     | Axis | Pick |
     |------|------|
     | VC portfolios | 3–5 of: Index, Balderton, Accel EU, Creandum, Atomico, Lakestar, Point Nine, La Famiglia, EQT, Northzone, Cherry, Earlybird, HV, Speedinvest, Molten |
     | Funding trackers | Sifted AI 100 (latest) + Dealroom recent EU AI rounds |
     | HN "Who is Hiring" | Latest monthly thread — filter EU + AI/ML |
     | Job board | One of: Wellfound, Otta, Berlin Startup Jobs, SwissDevJobs, ai-jobs.net |
     | Alumni / news | ETH AI Center, TU Munich, CDTM, Google Alerts for `"Series A" OR "Series B" AI agent Europe` |

   - The user may override — if they want to focus on a specific city or funding stage, tailor accordingly.

3. **Run axes sequentially — one at a time, not in parallel**

   For each axis:
   - Use `WebFetch` / `WebSearch` against the source.
   - Apply the profile filter from `context-5`: AI-native, Series A–C (or well-funded seed), <200 people, shipping product, EU / Remote-EU, recent funding.
   - Cross-reference every candidate against the pool (case-insensitive on `company`) **and** against candidates already added in this sweep.
   - Surface 8–15 matches per axis.
   - Present batched: `company · location · funding · backers · 1-line fit note · role URL (if found)`.
   - Flag stage-mismatches rather than drop silently.
   - Ask: **"Which add to the pool as `candidate`? Any to promote to `applied`?"**
   - Write approved rows to the pool table in `context-5` (the PostToolUse hook runs `uv run coop-os validate` — fix errors before moving on).
   - Move to next axis.

4. **Closing summary**
   - Total axes swept · total candidates added · top 5 picks with rationale.
   - Update `task-5`:
     - Add a dated entry under "This week's axes" (e.g. `2026-04-21 — Sweep: Index + Balderton + Sifted AI 100 + HN + ai-jobs.net → 42 new candidates`).
     - Mark swept axes as done; move remaining queued sources forward.
     - Capture any standout market signals under "Notes".

5. **Promote to `applied` (optional)**
   - If any new candidate has a specific open role the user wants to pursue now, create `coop_os/workspace/tasks/task-{next-id}-<Company> process/description.md` with `milestone: milestone-9`, `status: todo`.
   - Tone reference: existing `task-1-Altura process`, `task-4-Mistral process`.

## Defaults and guardrails

- **One axis at a time.** Parallel fetches fragment review.
- **Dedup is cumulative within the sweep.** Each axis's propose step checks against the pool + everything already added this session.
- **No fabrication.** `—` for unknown funding/backers. Mark the row for manual verification.
- **Stage-mismatches surfaced, not hidden.** Seed rounds with strong backers (e.g. Mirelo backed by Index + a16z) stay visible so the user can override.
- **Acquired / shut down** — status `archived`, one-line note (e.g. Humanloop → Anthropic, Jan 2026).

## When to run

- First-time setup (pool is empty).
- Quarterly refresh (pool feels stale, no new applications emerging).
- After a funding-news catalyst (e.g. a major round that signals a hiring wave).

For anything else, prefer `/scan-jobs` — short daily top-ups over large infrequent sweeps.
