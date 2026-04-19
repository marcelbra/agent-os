---
name: coop-session
description: Start a coop-os session. Scans workspace, loads personal context, and orients the agent. Use at the start of any session or to re-ground mid-session.
---

Read `coop_os/agent/AGENT.md` and follow the **Session Setup** section.
Spend ~15 seconds scanning all relevant files before presenting anything.
After presenting the status snapshot, wait for the user to direct the session.

## Presentation

Render the snapshot inside a single fenced code block using Unicode
box-drawing characters. The code fence preserves monospace alignment in the
Claude Code renderer; rounded corners (`╭ ╮ ╰ ╯`) and light horizontals
(`─ │`) give a dashboard feel without `===` noise.

Frame width: 78 columns (fits inside an 80-col terminal with margin).
One outer frame; single horizontal divider (`├──…──┤`) between sections.
Section headers ride on the divider line itself, left-padded.

Vertical breathing room: include one blank padding row (`│` + spaces + `│`)
immediately after the title, after every section divider, and before the
bottom edge. This keeps each section visually distinct without doubling
the height of the frame.

Title line shows both date and 24h local time — `YYYY-MM-DD · HH:MM`.

### Template

Replace bracketed placeholders. Omit a section entirely if it has no
content (e.g. no past-dated items) — drop that section's divider too, so
the frame stays tight.

````
```
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│  coop-os · session snapshot · [YYYY-MM-DD] · [HH:MM]                         │
│                                                                              │
├─ workspace ──────────────────────────────────────────────────────────────────┤
│                                                                              │
│  roles [N]  ·  milestones [N active / N done]  ·  tasks [N]  ·  contexts [N] │
│                                                                              │
├─ recurring habits ───────────────────────────────────────────────────────────┤
│                                                                              │
│  • [role]: [habit summary or "— gap —"]                                      │
│  • [role]: [habit summary or "— gap —"]                                      │
│                                                                              │
├─ due in the next ~30 days ───────────────────────────────────────────────────┤
│                                                                              │
│  [YYYY-MM-DD]  │  [milestone title]                      │  [role]           │
│  [YYYY-MM-DD]  │  [milestone title]                      │  [role]           │
│                                                                              │
├─ ⚠ past-dated ───────────────────────────────────────────────────────────────┤
│                                                                              │
│  [YYYY-MM-DD]  │  [item title]                           │  needs decision   │
│                                                                              │
├─ pending notes ──────────────────────────────────────────────────────────────┤
│                                                                              │
│  [N] unscanned in user/notes/   →  run /scan-notes                           │
│                                                                              │
├─ git ────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  branch: [name]   ·   [clean | N uncommitted changes]                        │
│                                                                              │
├─ open threads ───────────────────────────────────────────────────────────────┤
│                                                                              │
│  • [thread summary]                                                          │
│                                                                              │
├─ next moves ─────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. [concrete option]                                                        │
│  2. [concrete option]                                                        │
│  3. [concrete option]                                                        │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**What direction?**
````

### Rules

- Pad every content line with spaces so the trailing `│` lands in column 78.
- Truncate long titles with `…` rather than wrapping — keep one row per item.
- If a cell would overflow, shorten the title, not the frame.
- The closing `╰──…──╯` and the `**What direction?**` prompt always appear.
- Do not add fields beyond what AGENT.md Session Setup specifies.
- For the title timestamp, use the system's current local 24h time (e.g. `date +%H:%M`) at snapshot render time.
