# AI Screener – Git Workflow & Branching Strategy

**Document ID:** DOC-006

**Version:** 0.1.0-alpha

**Status:** Draft

---

# 1. Purpose

This document defines the Git workflow, branching strategy, versioning, and release process for AI Screener.

The objective is to maintain a clean, traceable, and scalable Git history.

---

# 2. Repository Structure

Default Branches

main

develop

Feature Branches

feature/*

Hotfix Branches

hotfix/*

Release Branches

release/*

---

# 3. Branch Responsibilities

## main

Production-ready code only.

Every commit in main should be deployable.

---

## develop

Integration branch.

Completed features are merged here first.

---

## feature/*

One functional module per branch.

Examples:

feature/market-data-engine

feature/indicator-engine

feature/scanner-engine

feature/backtesting

feature/dashboard

---

## hotfix/*

Used only to fix critical production issues.

---

## release/*

Optional branch for preparing major releases.

---

# 4. Sprint Strategy

Sprint 0

Single branch:

feature/project-foundation

Sprint 1+

One feature branch per module.

Each module includes:

* Documentation
* Code
* Tests
* Configuration updates

---

# 5. Commit Message Standard

Format

<type>(scope): description

Types

feat

fix

docs

refactor

test

chore

Examples

feat(scanner): implement stock scanner

fix(cpr): correct monthly CPR calculation

docs(hld): update architecture diagram

refactor(database): simplify repository pattern

test(indicators): add CPR unit tests

---

# 6. Pull Request Rules

Every Pull Request must include:

Purpose

Summary of Changes

Testing Performed

Documentation Updated

Known Limitations

Reviewer Checklist

---

# 7. Merge Policy

Feature Branch

↓

develop

↓

Regression Testing

↓

main

Never merge unfinished work directly into main.

---

# 8. Versioning

Semantic Versioning

Major.Minor.Patch

Examples

v0.1.0 Foundation

v0.2.0 Market Data

v0.3.0 Indicator Engine

v1.0.0 Beta

---

# 9. Tags

Each milestone release should be tagged.

Examples

v0.1.0-foundation

v0.2.0-market-data

v0.3.0-indicators

---

# 10. Sprint Completion Checklist

Before closing a sprint:

* Documentation complete
* Code reviewed
* Tests passing
* Git history clean
* Release notes updated
* Tag created

---

# 11. Branch Protection (Future)

Protect:

main

develop

Require:

* Pull Requests
* Passing tests
* Code review
* No direct pushes

---

# 12. Release Flow

Development

↓

Feature Complete

↓

Merge to develop

↓

Integration Testing

↓

Merge to main

↓

Git Tag

↓

Release Notes

---

# 13. Repository Principles

* Keep commits small and meaningful.
* Never commit secrets.
* Never commit generated files unless required.
* Update documentation alongside implementation.
* Every commit should move the project forward.

---

# 14. Git Philosophy

Git is not just version control.

It is the engineering history of AI Screener.

Every commit should tell part of the story of how the product evolved.
