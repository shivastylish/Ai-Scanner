# Contributing to AI Screener

Thank you for contributing to AI Screener.

Our goal is to build a production-grade AI-powered market research platform using modern software engineering practices.

---

# Project Vision

AI Screener is a modular market research platform supporting:

* Indian Equities
* Mutual Funds
* Crypto (planned)
* ETFs (planned)

The platform focuses on explainability, scalability, maintainability, and data quality.

---

# Engineering Principles

* Clean Architecture
* SOLID Principles
* DRY
* KISS
* Composition over Inheritance
* Explicit is better than implicit
* Testable code first

---

# Technology Stack

| Component       | Technology          |
| --------------- | ------------------- |
| Python          | 3.12–3.13           |
| Package Manager | uv                  |
| Configuration   | pydantic-settings   |
| Database        | SQLAlchemy + SQLite |
| Data Processing | pandas, NumPy       |
| Testing         | pytest              |
| Formatter       | black               |
| Linter          | ruff                |
| Import Sorting  | isort               |
| Type Checking   | mypy                |

---

# Repository Structure

```text
src/
    ai_screener/
        core/
        config/
        market_data/
        indicators/
        screening/
        scoring/
        explainability/
        backtesting/
        portfolio/
        journal/
        dashboard/
        utils/

tests/
docs/
scripts/
database/
data/
logs/
reports/
```

---

# Branch Strategy

* main → Production
* develop → Integration
* feature/* → Feature development
* bugfix/* → Bug fixes
* hotfix/* → Production fixes

No direct commits to `main`.

---

# Commit Convention

Use Conventional Commits.

Examples:

```text
feat(provider): implement Yahoo Finance provider
feat(database): implement SQLite persistence layer
fix(config): resolve database configuration issue
refactor(service): simplify provider registration
test(provider): add Yahoo provider tests
docs(readme): update setup guide
```

---

# Coding Standards

* Python type hints are mandatory.
* Use Google-style docstrings.
* Follow PEP 8.
* Keep functions focused on a single responsibility.
* Avoid global state.
* Avoid hardcoded configuration.
* Use dependency injection where appropriate.

---

# Configuration

* Never commit `.env`.
* Commit `.env.example`.
* Read configuration through `settings.py`.
* Never hardcode API keys or secrets.

---

# Testing Requirements

Every feature must include:

* Unit tests
* Integration tests (when applicable)

Before committing:

```bash
uv run pytest
```

---

# Definition of Done

A task is complete only if:

* Code builds successfully
* Tests pass
* Ruff passes
* Black formatting passes
* mypy passes
* Documentation updated
* No secrets committed
* Semantic commit created

---

# AI Agent Instructions

When implementing features:

1. Preserve the existing architecture.
2. Keep commits small and focused.
3. Do not modify unrelated files.
4. Add tests for new functionality.
5. Avoid introducing new dependencies without justification.
6. Use existing configuration and logging systems.
7. Follow the provider → pipeline → service → repository architecture.
8. Prefer composition over inheritance.
9. Never hardcode secrets.
10. If requirements are ambiguous, stop and request clarification instead of making assumptions.

---

# Pull Requests

Each pull request should:

* Solve a single problem.
* Reference the related issue.
* Include tests.
* Pass all quality checks.
* Update documentation if behavior changes.

---

# Code Review Checklist

* Architecture respected
* Naming is clear
* Tests added
* Logging included where appropriate
* Error handling implemented
* No duplicated logic
* Performance considered
* Documentation updated

---

Following these guidelines ensures AI Screener remains maintainable, scalable, and production-ready as it grows.
