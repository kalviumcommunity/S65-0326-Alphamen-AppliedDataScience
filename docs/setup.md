# Local Setup

## Python environment

This repository uses `uv` with `pyproject.toml` for dependency management.

1. Install Python 3.11 on your machine.
2. Install `uv` if it is not already available.
3. Sync the environment from the repository root:

```bash
uv sync
```

## Jupyter tools

Jupyter dependencies are declared in `pyproject.toml`, so running `uv sync` installs the notebook tooling required for this sprint.

## Verification commands

Use these commands after setup:

```bash
uv run python --version
uv run jupyter --version
uv run python -m ipykernel --version
```
