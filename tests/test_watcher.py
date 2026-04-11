"""Unit tests for FileSnapshot — the mtime-based file change detector."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from coop_os.tui.watcher import FileSnapshot


def _make_root(tmp_path: Path) -> Path:
    """Create a minimal workspace layout under tmp_path and return root."""
    (tmp_path / "coop_os" / "workspace").mkdir(parents=True)
    (tmp_path / "coop_os" / "user").mkdir(parents=True)
    (tmp_path / "coop_os" / "agent").mkdir(parents=True)
    return tmp_path


def test_build_tracks_md_files(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    md_file = root / "coop_os" / "workspace" / "role-1-Self.md"
    md_file.write_text("hello")
    txt_file = root / "coop_os" / "workspace" / "ignored.txt"
    txt_file.write_text("ignored")

    snapshot = FileSnapshot(root)
    snapshot.build()

    assert str(md_file) in snapshot._snapshot
    assert str(txt_file) not in snapshot._snapshot


def test_build_tracks_nested_md_files(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    task_dir = root / "coop_os" / "workspace" / "task-1-My Task"
    task_dir.mkdir()
    desc = task_dir / "description.md"
    desc.write_text("---\nid: task-1\ntitle: My Task\n---\n")

    snapshot = FileSnapshot(root)
    snapshot.build()

    assert str(desc) in snapshot._snapshot


def test_scan_detects_new_file(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    snapshot = FileSnapshot(root)
    snapshot.build()

    new_file = root / "coop_os" / "workspace" / "role-2-Health.md"
    new_file.write_text("new content")

    changed = snapshot.scan()

    assert str(new_file) in changed


def test_scan_detects_modified_file(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    md_file = root / "coop_os" / "workspace" / "role-1-Self.md"
    md_file.write_text("original")

    snapshot = FileSnapshot(root)
    snapshot.build()

    # Ensure mtime advances — sleep briefly if needed, or force via utime
    time.sleep(0.01)
    md_file.write_text("modified")

    changed = snapshot.scan()

    assert str(md_file) in changed


def test_scan_detects_removed_file(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    md_file = root / "coop_os" / "workspace" / "role-1-Self.md"
    md_file.write_text("content")

    snapshot = FileSnapshot(root)
    snapshot.build()

    md_file.unlink()

    changed = snapshot.scan()

    assert str(md_file) in changed


def test_scan_returns_empty_when_unchanged(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    md_file = root / "coop_os" / "workspace" / "role-1-Self.md"
    md_file.write_text("content")

    snapshot = FileSnapshot(root)
    snapshot.build()

    changed = snapshot.scan()

    assert changed == set()


def test_mark_written_suppresses_own_write(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    md_file = root / "coop_os" / "workspace" / "role-1-Self.md"
    md_file.write_text("original")

    snapshot = FileSnapshot(root)
    snapshot.build()

    time.sleep(0.01)
    md_file.write_text("updated by TUI")
    snapshot.mark_written(md_file)

    changed = snapshot.scan()

    assert str(md_file) not in changed


def test_ensure_tracked_prevents_false_external(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    snapshot = FileSnapshot(root)
    snapshot.build()

    new_file = root / "coop_os" / "workspace" / "note-1-Note 1.md"
    new_file.write_text("brand new")
    snapshot.ensure_tracked(new_file)

    changed = snapshot.scan()

    assert str(new_file) not in changed


def test_ensure_tracked_noop_for_existing(tmp_path: Path) -> None:
    """ensure_tracked must NOT advance mtime for already-tracked paths."""
    root = _make_root(tmp_path)
    md_file = root / "coop_os" / "workspace" / "role-1-Self.md"
    md_file.write_text("original")

    snapshot = FileSnapshot(root)
    snapshot.build()
    old_mtime = snapshot._snapshot[str(md_file)]

    time.sleep(0.01)
    md_file.write_text("modified externally")
    # ensure_tracked should NOT update the snapshot entry — real change must be detectable
    snapshot.ensure_tracked(md_file)

    assert snapshot._snapshot[str(md_file)] == old_mtime
    changed = snapshot.scan()
    assert str(md_file) in changed


def test_mark_renamed_updates_snapshot(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    old_file = root / "coop_os" / "workspace" / "role-1-old.md"
    old_file.write_text("content")

    snapshot = FileSnapshot(root)
    snapshot.build()

    new_file = root / "coop_os" / "workspace" / "role-1-New Title.md"
    old_file.rename(new_file)
    snapshot.mark_renamed(old_file, new_file)

    changed = snapshot.scan()

    assert str(old_file) not in changed
    assert str(new_file) not in changed


def test_scan_detects_externally_renamed_file(tmp_path: Path) -> None:
    """Renaming a .md file externally is detected as both old path removed and new path added."""
    root = _make_root(tmp_path)
    old_file = root / "coop_os" / "workspace" / "role-1-Old Title.md"
    old_file.write_text("---\nid: role-1\ntitle: Old Title\n---\n")

    snapshot = FileSnapshot(root)
    snapshot.build()

    new_file = root / "coop_os" / "workspace" / "role-1-New Title.md"
    old_file.rename(new_file)

    changed = snapshot.scan()

    assert str(old_file) in changed, "removed path must be reported as changed"
    assert str(new_file) in changed, "added path must be reported as changed"


def test_scan_detects_externally_renamed_task_dir(tmp_path: Path) -> None:
    """Renaming a task directory externally is detected via its description.md path change."""
    root = _make_root(tmp_path)
    old_dir = root / "coop_os" / "workspace" / "task-1-Old Task"
    old_dir.mkdir(parents=True)
    old_desc = old_dir / "description.md"
    old_desc.write_text("---\nid: task-1\ntitle: Old Task\n---\n")

    snapshot = FileSnapshot(root)
    snapshot.build()

    new_dir = root / "coop_os" / "workspace" / "task-1-New Task"
    old_dir.rename(new_dir)
    new_desc = new_dir / "description.md"

    changed = snapshot.scan()

    assert str(old_desc) in changed, "old description.md path must be reported as changed"
    assert str(new_desc) in changed, "new description.md path must be reported as changed"


def test_build_skips_git_and_cache_dirs(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    git_md = root / "coop_os" / "workspace" / ".git" / "COMMIT_EDITMSG.md"
    git_md.parent.mkdir(parents=True)
    git_md.write_text("should be ignored")
    real_md = root / "coop_os" / "workspace" / "role-1-Self.md"
    real_md.write_text("real")

    snapshot = FileSnapshot(root)
    snapshot.build()

    assert str(git_md) not in snapshot._snapshot
    assert str(real_md) in snapshot._snapshot
