# CLAUDE.md

Guidance for Claude Code working in this repository. This file is
operational notes only — it does not replace or duplicate the project's
own governance documents, which remain the source of truth:

- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — the binding architecture rules (Provider → Normalizer → Pipeline → Service → Repository → Database; no bypassing; per-layer responsibilities).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — engineering contract, branch strategy, Definition of Done.
- [`docs/07_Engineering/`](docs/07_Engineering/) — Git workflow, coding standards, documentation standards.
- [`docs/ADR/ADR-Index_v0.1.0.md`](docs/ADR/ADR-Index_v0.1.0.md) — accepted architecture decisions.

Read those before making non-trivial changes. If anything below conflicts
with them, those documents win.

## Commands

```bash
uv sync --extra dev          # install dependencies (including dev tools)
uv run pytest                # hermetic tests only (default; see Testing below)
uv run pytest -m live        # + the network-dependent smoke tests, run manually
uv run ruff check src tests scripts alembic
uv run black src tests scripts alembic
uv run isort src tests scripts alembic --profile black
uv run mypy src              # strict mode
uv run alembic revision --autogenerate -m "message"   # after changing an ORM model
uv run alembic upgrade head                              # apply migrations
```

## Testing

Tests are hermetic by default: an in-memory SQLite database and a fake
provider (`tests/fakes/fake_provider.py`) that never touches the network.
Shared fixtures live in `tests/conftest.py` (`db_engine`, `repository`,
`registered_fake_provider`, `service`) — reuse them for new tests instead
of hand-rolling a database or a stub provider.

Anything that must hit a live external service (a real Yahoo Finance call,
for example) is marked `@pytest.mark.live` and excluded from the default
run via `addopts` in `pyproject.toml`. Keep it that way: a new test should
only carry that marker if it genuinely cannot be faked, and it must never
write into the real `data/ai_screener.db`.

## Database schema changes

Alembic is the source of truth for schema (`alembic/`). After changing a
model in `src/ai_screener/database/models.py`, generate and review a
migration rather than relying on `Base.metadata.create_all()`.
`scripts/create_database.py` still exists for quick throwaway databases
but does not apply Alembic-only schema changes.

## Secrets

`.env` and the SQLite database/log files are gitignored — do not
re-commit them. Real API keys (crypto exchange keys especially, added in
later sprints) belong only in a local `.env`, never in `.env.example` or
committed anywhere.

## Roadmap

The active multi-sprint implementation plan lives at
`docs/07_Engineering/Roadmap_Sprint1_Through_Sprint9_v0.1.0.md`. Check it
before starting a new sprint's work — each sprint lists open questions to
confirm before implementation.
