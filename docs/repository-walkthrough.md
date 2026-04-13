# Repository Walkthrough

## Planned structure

- `docs/`: sprint planning, setup notes, lifecycle references, and project documentation
- `data/raw/`: unmodified source files used for reproducibility
- `data/processed/`: cleaned datasets ready for analysis
- `notebooks/`: exploratory work and learning notebooks
- `outputs/`: charts, exported reports, and analysis artifacts
- `scripts/`: runnable Python scripts for repeatable steps
- `src/`: reusable Python modules for the project

## How to read this repository

1. Start with `docs/plan.md` for the full project objective.
2. Use `README.md` to understand the sprint scope.
3. Follow notebooks and scripts in order as the data workflow grows.
4. Compare raw data, processed data, and outputs to understand how analysis changes the source data.

## Why this layout works for data projects

It separates source data, code, and outputs so the project stays reproducible and easier to review.
