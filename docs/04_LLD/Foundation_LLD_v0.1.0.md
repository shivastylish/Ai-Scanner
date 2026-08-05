# AI Screener – Foundation Low-Level Design (LLD)

**Document ID:** DOC-004
**Version:** 0.1.0-alpha
**Sprint:** Sprint 0
**Status:** Draft

---

# 1. Purpose

This document defines the implementation blueprint for AI Screener.

Unlike the High-Level Design, this document focuses on package structure, module responsibilities, interfaces, coding conventions, and implementation boundaries.

---

# 2. Design Principles

* Single Responsibility Principle (SRP)
* Open/Closed Principle (OCP)
* Dependency Inversion
* Modular Architecture
* Configuration First
* Testability by Design

---

# 3. Project Structure

```text
AI-Screener/

.github/
config/
data/
docs/
logs/
reports/
scripts/
src/
tests/

README.md
CHANGELOG.md
LICENSE
pyproject.toml
requirements.txt
```

---

# 4. Source Structure

```text
src/

core/
config/
data/
database/
indicators/
scanner/
ranking/
explainability/
backtesting/
dashboard/
portfolio/
journal/
alerts/
utils/
```

---

# 5. Module Responsibilities

## core/

Application bootstrap

Global constants

Dependency initialization

Exception handling

---

## config/

Application configuration

Environment loading

Runtime settings

---

## data/

Market data download

Validation

Transformation

Caching

---

## database/

Database connections

Repositories

Persistence

Migration support

---

## indicators/

Daily CPR

Weekly CPR

Monthly CPR

EMA

RSI

ATR

MACD

Future indicators

---

## scanner/

Scanning engine

Filtering

Rule execution

Candidate generation

---

## ranking/

Weighted scoring

Ranking logic

Confidence calculation

---

## explainability/

Reason generation

Score explanation

Risk explanation

Historical evidence summary

---

## backtesting/

Historical simulation

Performance metrics

Trade statistics

---

## dashboard/

Desktop UI

Charts

Reports

Watchlists

---

## portfolio/

Portfolio tracking

Risk exposure

Performance metrics

---

## journal/

Trade journal

Lessons learned

Screenshots

Notes

---

## alerts/

Future notification engine

Email

Desktop notifications

Messaging integrations

---

## utils/

Reusable helper functions

Formatting

Validation

Date utilities

---

# 6. Coding Conventions

Every module should expose a clear public interface.

Internal helper functions remain private.

Business logic must not depend directly on the UI.

Database access must be isolated from indicator calculations.

---

# 7. Dependency Rules

Allowed

UI → Services

Services → Domain

Domain → Infrastructure

Infrastructure → Database

Not Allowed

UI → Database

Indicators → UI

Scanner → Dashboard

Portfolio → Scanner

This prevents tight coupling.

---

# 8. Configuration Strategy

No hard-coded values.

Configuration must come from:

* config/
* environment variables
* settings files

---

# 9. Logging Strategy

Use structured logging.

Levels:

DEBUG

INFO

WARNING

ERROR

CRITICAL

Every exception must be logged with sufficient context.

---

# 10. Error Handling

Use custom exception classes.

Catch errors at application boundaries.

Never silently ignore failures.

---

# 11. Testing Strategy

Each module must include:

* Unit Tests
* Integration Tests (where applicable)

Future target:

High coverage for core business logic.

---

# 12. Naming Conventions

Folders

snake_case

Python Files

snake_case.py

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

---

# 13. Future Extensibility

The architecture should allow:

* New indicators
* New strategies
* Multiple exchanges
* Multiple databases
* Web application
* Mobile application

without requiring major redesign.

---

# 14. Definition of Ready

Before implementation begins:

* Requirements approved
* Design approved
* Inputs defined
* Outputs defined
* Acceptance criteria defined

---

# 15. Definition of Done

A module is complete only if:

* Code implemented
* Tests passed
* Documentation updated
* Review completed
* Acceptance criteria satisfied
* Git committed

---

# 16. Next Document

DOC-005 – Coding Standards

This document will define formatting rules, naming standards, documentation conventions, testing expectations, and code review requirements used throughout the project.
