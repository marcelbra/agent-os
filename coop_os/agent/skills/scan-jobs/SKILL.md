---
description: Daily morning scan for new AI/ML roles. Runs one rotating research axis per day, surfaces 2–5 candidates, and flags any in-flight process tasks that have gone stale. Designed to fit inside the morning check-in routine — 5–10 minutes.
name: scan-jobs
---

## Purpose

Keep the job-search pipeline moving one small step every weekday. Short, focused, and paired with a quick sanity check on in-flight processes so nothing rots.

For bootstrapping a fresh pool, use `/seed-jobs`. For a full tracking-sheet view, use `/track-jobs`.

## Required reading before running

- `coop_os/user/context/context-5-Job search profile & pool.md` — profile filter + pool (exclusion list).
- `coop_os/workspace/tasks/task-5-Job search research/description.md` — contains the **weekly rotation schedule** (which axis runs on which day).
- All `<Company> process` tasks under `coop_os/workspace/tasks/` — for the stale check.

## Steps

1. **Load context**
   - Read `context-5` and `task-5`.
   - List active `<Company> process` tasks (status `todo` or `in_progress`) under `milestone-9`.

2. **Pick today's axis from the rotation**
   - Read the rotation schedule in `task-5`. Default rotation (weekdays):

     | Day | Axis |
     |-----|------|
     | Monday | VC portfolio (rotate through Index → Balderton → Accel → Creandum → Atomico → Lakestar → …) |
     | Tuesday | HN "Who is Hiring" (latest thread) + recent YC batch |
     | Wednesday | Funding tracker (Dealroom / Crunchbase / Sifted AI 100) |
     | Thursday | Job board (rotate Wellfound → Otta → Berlin Startup Jobs → SwissDevJobs → ai-jobs.net) |
     | Friday | Alumni + funding-round news (Google Alerts for `"Series A" OR "Series B" AI agent Europe`) |

   - If today's slot says "VC portfolio" and the last-swept VC in `task-5` was Index, run Balderton next. Keep the rotation moving.
   - If the user requests a specific axis, override.

3. **Mini-sweep**
   - Use `WebFetch` / `WebSearch` against today's source only.
   - Apply the profile filter + dedup against the pool (case-insensitive on `company`).
   - Target **2–5 net-new candidates**. If nothing matches, that's a valid result — record it and move on.

4. **Propose additions**
   - Present: `company · location · funding · backers · 1-line fit note · role URL (if found)`.
   - Flag stage-mismatches.
   - Ask: **"Add to the pool?"**

5. **Write approved rows**
   - Append to the pool table in `context-5` with `status: candidate` and `researched_on: <today>`.
   - Hook runs `uv run coop-os validate` — fix errors before moving on.

6. **Stale check on in-flight processes**
   - For each active `<Company> process` task, look at the last modified timestamp of `description.md` and of any phase subtasks under it.
   - **Flag any process with no change in >7 days.**
   - Ask: **"Any movement on these? Anything to mark `done` / `cancelled` / rescheduled?"**
   - If the user reports movement, update the relevant task file(s) + the pool row status.
   - If a new interview phase got scheduled, create a nested subtask under the process directory (see "Process convention" in `context-5`).

7. **Log the scan in task-5**
   - Append a one-line entry under "This week's axes" in `task-5`:
     `2026-04-21 Mon — VC: Balderton → 3 new candidates; stale: ventai.ai (7 days, no movement)`
   - Advance the rotation marker if applicable.

8. **Wrap up**
   - 1-line summary: axis, candidates added, stale processes flagged.
   - If running inside `/check-in`, hand control back silently. If standalone, suggest `/check-in` if not done today.

## Defaults and guardrails

- **No axis skipping without a reason.** If today's axis yielded zero candidates, log `→ 0 new` and move on. Don't silently re-run yesterday's axis to pad the number.
- **Dedup is authoritative.** The pool is the exclusion list. Never re-propose a company already listed.
- **Stale threshold is 7 days for active processes, 14 days before aggressive prompting.** Don't nag the user on a 3-day-old entry.
- **No fabrication.** `—` for unknown fields.

## When NOT to run

- No active processes + empty pool → run `/seed-jobs` first.
- Mid-sweep (already running `/seed-jobs` today) → skip, the seed covers it.
- Weekend → optional; rotation assumes weekdays.
