# Personal skills

Drop-in directory for **personal** skills — ones that reference your own data under `coop_os/user/` or `coop_os/workspace/` and wouldn't be useful to anyone else.

Everything in this directory is gitignored except this README. Any `<slug>/SKILL.md` you add stays local to your machine and never ships with the PyPI package.

## Adding a personal skill

```
mkdir -p coop_os/user/skills/my-skill
$EDITOR coop_os/user/skills/my-skill/SKILL.md
make skills
```

`make skills` installs shared skills from `coop_os/agent/skills/` and then — if this directory has anything besides the README — installs personal skills from here too. Both land in `.claude/skills/` for the agent harness to discover.

## When to put a skill here vs. in `coop_os/agent/skills/`

- **`coop_os/agent/skills/`** — useful to everyone. References only shared code/docs, no personal data. Tracked in git and ships to PyPI.
- **`coop_os/user/skills/`** — references *your* `coop_os/user/context/*`, `coop_os/workspace/tasks/*`, `milestones/*`, etc. Not tracked, not shipped.

A skill whose "Required reading" section points at a gitignored file almost certainly belongs here.
