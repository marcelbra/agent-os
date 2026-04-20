---
description: Render the job-search tracking sheet — pool summary, active processes, scheduled interview phases, and staleness flags — then prompt to maintain any inconsistent or out-of-date entries. Use ad-hoc or during weekly review.
name: track-jobs
---

## Purpose

One stop for "what's the state of my job search right now?". Combines the pool (`context-5`) with the process tasks (`milestone-9`) and their interview phase subtasks into a single view, and surfaces anything that looks out of date or inconsistent.

For discovery, use `/seed-jobs` (big sweep) or `/scan-jobs` (daily top-up).

## Required reading before running

- `coop_os/user/context/context-5-Job search profile & pool.md` — the pool.
- All `<Company> process` tasks under `coop_os/workspace/tasks/` and any nested phase subtasks.
- `coop_os/workspace/milestones/milestone-9-Switch jobs — target 130-140k gross.md` — the milestone header (deadline).

## Steps

1. **Load state**
   - Parse the pool table from `context-5`. Tally by `status`.
   - List every `<Company> process` task under `milestone-9`, including nested phase subtasks.
   - Compute last-modified timestamps for each process task (newest of `description.md` or any subtask).

2. **Render the dashboard**

   Use Unicode box-drawing consistent with `/coop-session`. Width 78 cols. Sections:

   ```
   ╭─ job search · YYYY-MM-DD · HH:MM ───────────────────────────────────────────╮
   │                                                                              │
   │  milestone-9  ·  deadline YYYY-MM-DD  ·  N days left                         │
   │                                                                              │
   ├─ pool ──────────────────────────────────────────────────────────────────────┤
   │  candidate N   ·   applied N   ·   rejected N   ·   archived N               │
   │                                                                              │
   ├─ active processes ──────────────────────────────────────────────────────────┤
   │  company           │  current phase        │  status         │  last touch  │
   │  Mistral           │  Phase 2 — technical  │  in_progress    │  2d ago      │
   │  Altura            │  (no phase)           │  todo           │  15d ago ⚠   │
   │                                                                              │
   ├─ upcoming phases ───────────────────────────────────────────────────────────┤
   │  YYYY-MM-DD        │  company              │  phase                          │
   │                                                                              │
   ├─ stale ─────────────────────────────────────────────────────────────────────┤
   │  • <Company> process — no updates in Nd                                      │
   │                                                                              │
   ├─ inconsistencies ───────────────────────────────────────────────────────────┤
   │  • Pool row X marked `applied` but no <X> process task exists                │
   │  • <Y> process task has no matching pool row                                 │
   │                                                                              │
   ╰──────────────────────────────────────────────────────────────────────────────╯
   ```

   Omit any section that's empty.

3. **Detect inconsistencies**
   - Pool rows with `status: applied` but no matching `<Company> process` task under `milestone-9`.
   - `<Company> process` tasks whose company has no pool row (or a non-`applied` pool row).
   - Process tasks in status `in_progress` with no phase subtasks.
   - Phase subtasks missing `start_date` or with past `start_date` but no debrief in the body.

4. **Flag staleness**
   - Active process with no change in >14 days → flag for decision.
   - Scheduled phase date in the past → flag (interview happened, needs debrief or status update).

5. **Prompt maintenance**
   - Walk through each flagged item and ask: **"Update? Mark complete? Reschedule? Skip?"**
   - Apply approved edits:
     - Pool row status change → edit `context-5` table.
     - Process task status / body update → edit `description.md`.
     - Phase subtask debrief → edit subtask `description.md`.
     - Missing pool row → append.
     - Missing process task → offer to create (see `/seed-jobs` step 5 for template).
   - The PostToolUse hook runs `uv run coop-os validate` after every write — fix any parse error before moving on.

6. **Suggest next actions**
   - If a process has been stale for >14 days → suggest `mark as rejected` or `ping the recruiter`.
   - If a process has no active phase but status is `in_progress` → suggest creating the next phase subtask.
   - If the pool has <5 active candidates not yet applied to → suggest running `/scan-jobs` or `/seed-jobs`.

## Defaults and guardrails

- **Read-only by default.** Writes only happen on user confirmation per flagged item.
- **Staleness threshold**: 14 days for active processes (more lenient than `/scan-jobs` 7-day threshold — this skill is weekly, not daily).
- **Never silently fix inconsistencies.** Always confirm with the user. The user's state of mind about a process is the source of truth; the files follow.
- **Don't over-render.** If a section is empty, omit it — the dashboard should scan in 5 seconds, not 30.

## When to run

- Weekly (e.g. in `/weekly-review` or ad-hoc Sunday evening).
- Before a `/check-in` session where job-search work is the focus.
- After any week with ≥2 interviews — consolidates debriefs.
