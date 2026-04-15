# Repository Guidelines

## Project Structure & Module Organization

- Core app code lives in `src/ruz_server/`.
- API layer in `src/ruz_server/api/` (FastAPI routers and endpoints).
- Service/business logic in `src/ruz_server/services/`.
- Helper utilities in `src/ruz_server/helpers/`.
- DB and models in `src/ruz_server/database/` and related model modules.
- Compatibility entrypoint package in `src/ruzserver/`.
- Tests live in `tests/`, usually mirroring `src/ruz_server/` by domain.
- API docs and endpoint docs in `docs/`.

## Build, Test, and Development Commands

- Use venv: `.\.venv\Scripts\activate`
- Install runtime deps: `pip install -e .` or `pip install -e ".[test,dev]` for development
- Run app: `python -m ruzserver`
- Run all tests: `python -m pytest -q`
- Optional Make shortcuts (if `make` available): `make test`, `make test-api`, `make test-fast`
- Build Docker image: `docker build -t ruz-server .`

## Coding Style & Naming Conventions

- Python target version: 3.12.
- Ruff is configured in `pyproject.toml`; keep code Ruff-clean.
- Max line length: 88.
- Prefer type hints on public functions and service boundaries.
- Use `snake_case` for functions, variables, and module names.
- Use `PascalCase` for classes and Pydantic/SQLModel schemas.
- Keep API handlers thin; move business logic to `services/` and `helpers/`.
- Prefer explicit, domain-oriented names over generic names.
- Do not commit generated artifacts (`__pycache__`, `.pyc`, local caches, logs).

## Testing Guidelines

- Test framework: `pytest` with markers configured in `pyproject.toml`.
- Main command for this repo: `.\.venv\Scripts\pytest -q` (do not use global `pytest`).
- Place tests under `tests/` with file pattern `test_*.py`.
- Name tests as `test_<behavior>()`; keep one clear behavior/assertion focus per test.
- Use markers where relevant: `api`, `repositories`, `helpers`, `models`, `ruzapi`, `unit`, `integration`, `slow`.
- For changed logic, add/adjust tests in matching domain folder (API change -> `tests/api`, service change -> `tests/services`).
- Keep async tests compatible with `pytest-asyncio` configuration from `pyproject.toml`.

## Ruff Code Quality & Formatting

- Check code quality with Ruff): `.\.venv\Scripts\ruff check .`
- Auto-format code with Ruff: `.\.venv\Scripts\ruff format .`