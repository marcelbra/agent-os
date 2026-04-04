from __future__ import annotations

import re
import shutil
from pathlib import Path

import frontmatter

from agent_os.models import PMS, Milestone, Note, ParseError, ProjectState, Role, Task


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:40]


def _next_id(ids: list[str]) -> str:
    nums = [int(i) for i in ids if i.isdigit()]
    return str(max(nums, default=0) + 1)


def _read_fm(path: Path) -> tuple[dict, str]:
    post = frontmatter.load(str(path))
    return dict(post.metadata), post.content


def _write_fm(path: Path, metadata: dict, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(content, **metadata)
    path.write_text(frontmatter.dumps(post), encoding="utf-8")


# ── readers ───────────────────────────────────────────────────────────────────


def read_pms(root: Path) -> tuple[PMS | None, ParseError | None]:
    path = root / "context" / "0-pms.md"
    if not path.exists():
        return None, ParseError(file="context/0-pms.md", error="Required file missing")
    try:
        meta, content = _read_fm(path)
        return PMS(id="pms", title=meta.get("title", "Personal Mission Statement"), content=content), None
    except Exception as e:
        return None, ParseError(file="context/0-pms.md", error=str(e))


def read_roles(root: Path) -> tuple[list[Role], list[ParseError]]:
    roles: list[Role] = []
    errors: list[ParseError] = []
    roles_dir = root / "context" / "roles"
    if not roles_dir.exists():
        return roles, errors
    for path in sorted(roles_dir.glob("*.md")):
        try:
            meta, content = _read_fm(path)
            roles.append(
                Role(
                    id=str(meta["id"]),
                    name=str(meta["name"]),
                    emoji=str(meta["emoji"]),
                    title=str(meta["title"]),
                    content=content,
                )
            )
        except Exception as e:
            errors.append(ParseError(file=f"context/roles/{path.name}", error=str(e)))
    return roles, errors


def read_milestones(root: Path) -> tuple[list[Milestone], list[ParseError]]:
    milestones: list[Milestone] = []
    errors: list[ParseError] = []
    ms_dir = root / "milestones"
    if not ms_dir.exists():
        return milestones, errors
    for path in sorted(ms_dir.glob("*.md")):
        try:
            meta, content = _read_fm(path)
            milestones.append(
                Milestone(
                    id=str(meta["id"]),
                    title=str(meta["title"]),
                    role=str(meta.get("role", "")),
                    start_date=str(meta.get("start_date", "")),
                    end_date=str(meta.get("end_date", "")),
                    status=meta.get("status", "active"),
                    description=content,
                )
            )
        except Exception as e:
            errors.append(ParseError(file=f"milestones/{path.name}", error=str(e)))
    return milestones, errors


def read_tasks(root: Path) -> tuple[list[Task], list[ParseError]]:
    tasks: list[Task] = []
    errors: list[ParseError] = []
    tasks_dir = root / "tasks"
    if not tasks_dir.exists():
        return tasks, errors
    for task_dir in sorted(d for d in tasks_dir.iterdir() if d.is_dir()):
        desc_path = task_dir / "description.md"
        if not desc_path.exists():
            errors.append(ParseError(file=f"tasks/{task_dir.name}", error="Missing description.md"))
            continue
        try:
            meta, content = _read_fm(desc_path)
            tasks.append(
                Task(
                    id=str(meta["id"]),
                    title=str(meta["title"]),
                    status=meta.get("status", "todo"),
                    milestone=str(meta["milestone"]) if meta.get("milestone") else None,
                    labels=list(meta.get("labels", [])),
                    dependencies=[str(d) for d in meta.get("dependencies", [])],
                    created_date=str(meta.get("created_date", "")),
                    description=content,
                )
            )
        except Exception as e:
            errors.append(ParseError(file=f"tasks/{task_dir.name}/description.md", error=str(e)))
    return tasks, errors


def read_notes(root: Path) -> tuple[list[Note], list[ParseError]]:
    notes: list[Note] = []
    errors: list[ParseError] = []
    notes_dir = root / "notes"
    if not notes_dir.exists():
        return notes, errors
    for path in sorted(p for p in notes_dir.glob("*.md")):
        try:
            meta, content = _read_fm(path)
            notes.append(
                Note(
                    id=str(meta["id"]),
                    title=str(meta["title"]),
                    date=str(meta.get("date", "")),
                    scanned=bool(meta.get("scanned", False)),
                    content=content,
                )
            )
        except Exception as e:
            errors.append(ParseError(file=f"notes/{path.name}", error=str(e)))
    return notes, errors


def read_project(root: Path) -> ProjectState:
    pms, pms_err = read_pms(root)
    roles, role_errs = read_roles(root)
    milestones, ms_errs = read_milestones(root)
    tasks, task_errs = read_tasks(root)
    notes, note_errs = read_notes(root)
    errors = ([pms_err] if pms_err else []) + role_errs + ms_errs + task_errs + note_errs
    return ProjectState(pms=pms, roles=roles, milestones=milestones, tasks=tasks, notes=notes, errors=errors)


# ── writers ───────────────────────────────────────────────────────────────────


def write_pms(root: Path, pms: PMS) -> None:
    _write_fm(root / "context" / "0-pms.md", {"id": "pms", "title": pms.title}, pms.content)


def write_role(root: Path, role: Role) -> None:
    roles_dir = root / "context" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_file_by_id(roles_dir, role.id)
    path = existing or roles_dir / f"{role.id}-{slugify(role.name)}.md"
    _write_fm(path, {"id": role.id, "name": role.name, "emoji": role.emoji, "title": role.title}, role.content)


def write_milestone(root: Path, ms: Milestone) -> None:
    ms_dir = root / "milestones"
    ms_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_file_by_id(ms_dir, ms.id)
    path = existing or ms_dir / f"{ms.id}-{slugify(ms.title)}.md"
    _write_fm(
        path,
        {
            "id": ms.id,
            "title": ms.title,
            "role": ms.role,
            "start_date": ms.start_date,
            "end_date": ms.end_date,
            "status": str(ms.status),
        },
        ms.description,
    )


def write_task(root: Path, task: Task) -> None:
    tasks_dir = root / "tasks"
    existing_dir = _find_task_dir(tasks_dir, task.id)
    task_dir = existing_dir or tasks_dir / f"{task.id}-{slugify(task.title)}"
    task_dir.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "id": task.id,
        "title": task.title,
        "status": str(task.status),
        "created_date": task.created_date,
        "labels": task.labels,
        "dependencies": task.dependencies,
    }
    if task.milestone:
        meta["milestone"] = task.milestone
    _write_fm(task_dir / "description.md", meta, task.description)


def write_note(root: Path, note: Note) -> None:
    notes_dir = root / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_file_by_id(notes_dir, note.id)
    path = existing or notes_dir / f"{note.id}-{slugify(note.title)}.md"
    _write_fm(path, {"id": note.id, "title": note.title, "date": note.date, "scanned": note.scanned}, note.content)


# ── deleters ──────────────────────────────────────────────────────────────────


def delete_role(root: Path, role_id: str) -> bool:
    path = _find_file_by_id(root / "context" / "roles", role_id)
    if path:
        path.unlink()
        return True
    return False


def delete_milestone(root: Path, ms_id: str) -> bool:
    path = _find_file_by_id(root / "milestones", ms_id)
    if path:
        path.unlink()
        return True
    return False


def delete_task(root: Path, task_id: str) -> bool:
    d = _find_task_dir(root / "tasks", task_id)
    if d:
        shutil.rmtree(d)
        return True
    return False


def delete_note(root: Path, note_id: str) -> bool:
    path = _find_file_by_id(root / "notes", note_id)
    if path:
        path.unlink()
        return True
    return False


# ── ID generation ─────────────────────────────────────────────────────────────


def next_role_id(root: Path) -> str:
    d = root / "context" / "roles"
    return _next_id([_fm_id(p) for p in d.glob("*.md")] if d.exists() else [])


def next_milestone_id(root: Path) -> str:
    d = root / "milestones"
    return _next_id([_fm_id(p) for p in d.glob("*.md")] if d.exists() else [])


def next_task_id(root: Path) -> str:
    d = root / "tasks"
    if not d.exists():
        return "1"
    ids = [_fm_id(td / "description.md") for td in d.iterdir() if td.is_dir() and (td / "description.md").exists()]
    return _next_id(ids)


def next_note_id(root: Path) -> str:
    d = root / "notes"
    return _next_id([_fm_id(p) for p in d.glob("*.md")] if d.exists() else [])


# ── internals ─────────────────────────────────────────────────────────────────


def _fm_id(path: Path) -> str:
    try:
        meta, _ = _read_fm(path)
        return str(meta.get("id", ""))
    except Exception:
        return ""


def _find_file_by_id(directory: Path, item_id: str) -> Path | None:
    if not directory.exists():
        return None
    return next((p for p in directory.glob("*.md") if _fm_id(p) == item_id), None)


def _find_task_dir(tasks_dir: Path, task_id: str) -> Path | None:
    if not tasks_dir.exists():
        return None

    def _match(d: Path) -> bool:
        return d.is_dir() and (d / "description.md").exists() and _fm_id(d / "description.md") == task_id

    return next((d for d in tasks_dir.iterdir() if _match(d)), None)


def find_item_path(root: Path, kind: str, item_id: str) -> Path | None:
    """Return the file path for the given item kind and id."""
    match kind:
        case "pms":
            p = root / "context" / "0-pms.md"
            return p if p.exists() else None
        case "role":
            return _find_file_by_id(root / "context" / "roles", item_id)
        case "milestone":
            return _find_file_by_id(root / "milestones", item_id)
        case "task":
            d = _find_task_dir(root / "tasks", item_id)
            return d / "description.md" if d else None
        case "note":
            return _find_file_by_id(root / "notes", item_id)
    return None
