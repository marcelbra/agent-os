# Contributing

## Branches

| Branch | Purpose |
|--------|---------|
| `develop` | Integration branch — all PRs target this |
| `main` | Release branch — every merge triggers a PyPI publish |

Never push directly to `develop` or `main`. All changes go through PRs.

## Workflow

1. Branch off `develop`:
   ```
   git checkout -b feature/<slug> origin/develop
   ```
2. Make focused, atomic commits
3. Open a PR against `develop`
4. CI must pass before merging

### Branch naming

| Type | Pattern |
|------|---------|
| Feature | `feature/<slug>` |
| Bug fix | `fix/<slug>` |
| Chore / cleanup | `chore/<slug>` |

## Releasing

Only maintainers release. To publish a new version to PyPI:

1. Bump `version` in `pyproject.toml` on `develop`
2. Open a PR from `develop` → `main` titled `Release vX.Y.Z`
3. Merge with a merge commit (not squash)
4. The release workflow auto-tags `vX.Y.Z` and publishes to PyPI

## Development

```
make install   # install dependencies
make check     # lint + tests (run before opening a PR)
make run       # start the TUI
```
