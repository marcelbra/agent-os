![agent-os banner](banner.png)

A personal life OS that lives in your terminal. Markdown files as the database, a keyboard-driven TUI as the interface, and Claude as the AI co-pilot.

## What it is

agent-os organizes your life across five areas — Context, Milestones, Tasks, Notes, and Skills — all backed by plain markdown files with YAML frontmatter. No database, no sync, no lock-in.

The TUI lets you browse, edit, and create everything from the keyboard. `AGENT.md` defines how your AI agent operates — it ships with the repo and is fully editable from within the TUI.

## Structure

```
context/          # Personal Mission Statement + Roles
milestones/       # Long-horizon goals
tasks/            # Actionable items (each task is a directory)
notes/            # Logs, reflections, anything else
skills/           # Agent skill definitions (markdown)
AGENT.md          # AI co-pilot driver file
```

## Install

```bash
uv sync
uv run agent-os
```

Requires Python 3.13+.

## Keybindings

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate tree |
| `→` | Expand / enter section |
| `←` | Collapse / go to parent |
| `Enter` | Open item |
| `←` (in editor) | Return to tree (auto-saves) |
| `n` | New item |
| `d` | Delete item |
| `r` | Refresh |

## Tech

- [Textual](https://github.com/Textualize/textual) — TUI framework
- [python-frontmatter](https://github.com/eyeseast/python-frontmatter) — markdown + YAML parsing
- [Pydantic](https://docs.pydantic.dev/) — data models
