# VCT EMEA Kickoff Simulator (Streamlit)

A small personal Streamlit app to **simulate VCT EMEA Kickoff (2026)** in a **triple‑elimination** format and to build a **worst → best** ranking interactively.

> This repository is designed to be **clean, reproducible, and GitHub‑ready** (even as a small personal project): pinned tooling, consistent structure, and safe defaults.

## What’s inside

- **Kickoff bracket simulator** (triple-elimination, BO3/BO5 rules)
- **Worst → Best ranker** (you pick winners, winners are removed until one “worst” remains; repeat)

## Quickstart

### 1) Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -U pip
pip install -e .
```

### 2) Run the app

```bash
streamlit run streamlit_app/Home.py
```

Streamlit will open in your browser with:
- **Home**: bracket simulator
- **Page 1**: worst → best ranker

## Project structure

```text
vct-emea-kickoff-simulator/
├── streamlit_app/
│   ├── Home.py
│   └── pages/
│       └── 01_Worst_to_Best_Ranker.py
├── src/
│   └── __init__.py
├── .gitignore
├── .pre-commit-config.yaml
└── pyproject.toml
```

## Development (optional but recommended)

### Pre-commit (format + lint)

```bash
pip install pre-commit
pre-commit install
pre-commit run -a
```

### Lint/format manually

```bash
ruff check .
ruff format .
```

## Notes

- Team lists and matchups are hardcoded for the personal Kickoff simulation.
- No external data is required.

## License

Personal project — choose a license if you plan to share beyond private use.
