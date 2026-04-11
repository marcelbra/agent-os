from __future__ import annotations

import os
from pathlib import Path

_SKIP_DIRS: frozenset[str] = frozenset({".git", "__pycache__", ".mypy_cache", ".ruff_cache"})


class FileSnapshot:
    """Tracks mtime_ns for all .md files under the watched workspace directories.

    Used by the TUI poll loop to detect external changes (agent writes, manual edits)
    without false positives from the TUI's own writes.

    Typical usage:
    1. Call build() once at startup to initialise the baseline snapshot.
    2. Call scan() on each poll tick — it returns the set of paths that changed,
       were added, or were removed since the previous scan.
    3. Call mark_written(path) immediately after the app itself writes a file so
       the next scan does not treat that write as an external change.
    4. Call ensure_tracked(path) after creating a new file before entering edit
       mode, so the first watcher tick does not see the new file as external.
    5. Call mark_renamed(old, new) after a rename to update the snapshot entries
       without triggering a false external-change report.
    """

    def __init__(self, root: Path) -> None:
        self._watch_dirs: list[Path] = [
            root / "coop_os" / "workspace",
            root / "coop_os" / "user",
            root / "coop_os" / "agent",
        ]
        self._snapshot: dict[str, int] = {}

    def build(self) -> None:
        """Take the initial baseline snapshot. Call once after on_mount."""
        self._snapshot = self._collect()

    def scan(self) -> set[str]:
        """Rescan and return paths changed since the last scan.

        A path is included if: its mtime changed, it is new, or it was removed.
        Returns an empty set when nothing changed. Updates internal snapshot.
        """
        current = self._collect()
        all_keys = set(current) | set(self._snapshot)
        changed = {key for key in all_keys if current.get(key) != self._snapshot.get(key)}
        self._snapshot = current
        return changed

    def mark_written(self, path: Path) -> None:
        """Advance the snapshot entry for path to its current mtime.

        Call immediately after the TUI writes a file so the next scan does not
        treat that write as an external change.
        """
        path_str = str(path)
        try:
            self._snapshot[path_str] = os.stat(path_str).st_mtime_ns
        except OSError:
            pass

    def ensure_tracked(self, path: Path) -> None:
        """Add path to the snapshot only if not already present.

        Call when the TUI creates a new file (e.g. action_new_item) before
        entering edit mode. Prevents the first watcher tick from seeing the
        freshly created file as an external change and kicking the user out
        of edit mode.
        For already-tracked paths this is a no-op — it does NOT update mtime —
        so real external changes on that path are still detected correctly.
        """
        path_str = str(path)
        if path_str not in self._snapshot:
            try:
                self._snapshot[path_str] = os.stat(path_str).st_mtime_ns
            except OSError:
                pass

    def mark_renamed(self, old_path: Path, new_path: Path) -> None:
        """Update snapshot after a file rename.

        Removes the old path entry and records the new path at its current
        mtime. Prevents the watcher from reporting the rename as an external
        add/remove pair.
        """
        self._snapshot.pop(str(old_path), None)
        new_path_str = str(new_path)
        try:
            self._snapshot[new_path_str] = os.stat(new_path_str).st_mtime_ns
        except OSError:
            pass

    # ── Internal ──────────────────────────────────────────────────────────────

    def _collect(self) -> dict[str, int]:
        """Walk all watched directories and collect mtime_ns for every .md file."""
        result: dict[str, int] = {}
        for watch_dir in self._watch_dirs:
            if not watch_dir.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(watch_dir):
                dirnames[:] = [dirname for dirname in dirnames if dirname not in _SKIP_DIRS]
                for filename in filenames:
                    if not filename.endswith(".md"):
                        continue
                    full_path = os.path.join(dirpath, filename)
                    try:
                        result[full_path] = os.stat(full_path).st_mtime_ns
                    except OSError:
                        pass  # file disappeared mid-scan — skip silently
        return result
