# AI Screener – Coding Standards

**Document ID:** DOC-005

**Version:** 0.1.0-alpha

**Status:** Draft

---

# 1. Purpose

This document defines the coding standards that must be followed throughout the AI Screener project.

The objective is to ensure:

* Readability
* Maintainability
* Consistency
* Scalability
* Testability

---

# 2. Python Version

Python 3.12+

---

# 3. Formatting Standard

Formatter

Black

Maximum Line Length

88 characters

Import Sorting

isort

Linting

Ruff

Static Type Checking

mypy

---

# 4. Naming Convention

## Files

snake_case.py

Example

market_data_service.py

---

## Classes

PascalCase

Example

MarketDataService

CPREngine

ScannerEngine

---

## Functions

snake_case

Example

calculate_monthly_cpr()

scan_all_stocks()

---

## Variables

snake_case

Example

monthly_cpr

scanner_result

---

## Constants

UPPER_CASE

Example

DEFAULT_TIMEOUT

MAX_WORKERS

---

# 5. Folder Naming

Always

snake_case

No spaces

No abbreviations unless widely accepted.

---

# 6. Type Hints

Every public function must include type hints.

Example

def calculate_cpr(data: pd.DataFrame) -> CPRResult

---

# 7. Docstrings

Every public class and function must include a docstring.

Preferred style

Google Style Docstrings

---

# 8. Comments

Comments should explain **why**, not **what**.

Good

Explain business rules.

Bad

Repeat the code.

---

# 9. Logging

Never use print() for application logging.

Use the logging framework.

Levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

---

# 10. Exception Handling

Catch only expected exceptions.

Never use:

except:

Always catch specific exceptions.

---

# 11. Configuration

No hard-coded values.

All configurable values belong in:

config/

Environment Variables

Configuration Files

---

# 12. Database Access

Business logic must never directly execute SQL.

Use repository classes.

---

# 13. Module Responsibilities

Every module must have a single responsibility.

No mixed responsibilities.

---

# 14. Testing

Every public function should have corresponding unit tests.

Bug fixes should include regression tests where appropriate.

---

# 15. Code Review Checklist

Before merging:

* Code compiles
* Tests pass
* Documentation updated
* Type hints present
* Logging added where needed
* No duplicated code
* Naming standards followed

---

# 16. Git Commit Format

Examples

feat(scanner): add CPR scanner

fix(cpr): correct monthly CPR calculation

docs(hld): update architecture

refactor(database): simplify repository layer

test(scanner): add scanner unit tests

---

# 17. Pull Request Requirements

Every PR must include:

Purpose

Summary

Test Results

Documentation Changes

Known Limitations

---

# 18. Definition of Good Code

Good code is:

* Readable
* Simple
* Testable
* Reusable
* Well documented

---

# 19. Coding Philosophy

Code is written for humans first.

Computers execute it.

Developers maintain it.

---

# 20. Motto

Clean code today prevents technical debt tomorrow.
