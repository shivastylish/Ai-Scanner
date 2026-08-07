# AI Screener - AI Coding Agent Instructions

This document provides instructions for AI coding agents (GitHub Copilot, Codex, ChatGPT, etc.) contributing to AI Screener.

---

# Project Goal

AI Screener is an enterprise-grade AI-powered market research platform.

Current scope:

* Indian Equities
* Mutual Funds

Future scope:

* Crypto
* ETFs
* Commodities
* Forex

---

# Primary Objective

Write maintainable, production-quality code.

Correct architecture is more important than writing code quickly.

---

# Engineering Principles

Always follow:

* SOLID
* Clean Architecture
* Repository Pattern
* Provider Pattern
* Service Layer
* Dependency Injection
* DRY
* KISS

---

# Project Architecture

Market data flows in this order:

Provider

↓

Normalizer

↓

Pipeline

↓

Service

↓

Repository

↓

Database

No module should bypass this flow.

---

# Responsibilities

## Providers

Responsible only for fetching raw data.

Never save to the database.

Never perform business logic.

---

## Normalizers

Convert provider-specific responses into the standard internal schema.

---

## Pipeline

Responsible for:

* validation
* enrichment
* transformation

---

## Services

Services orchestrate business logic.

They may call:

* providers
* repositories
* pipelines

Repositories should never be called directly from UI or future scanner modules.

---

## Repository

Repositories are responsible only for persistence.

Repositories should not contain business logic.

---

# Standard Market Data Schema

Every provider must return data using these fields:

* symbol
* datetime
* open
* high
* low
* close
* volume
* asset_type
* provider
* exchange
* currency

Do not introduce provider-specific column names outside the provider layer.

---

# Folder Rules

New features must be placed in the correct package.

Avoid creating miscellaneous utility folders.

Keep the existing project layout.

---

# Configuration

Never hardcode:

* API keys
* secrets
* database paths

Read configuration from:

```
settings.py
```

Environment variables come from:

```
.env
```

Never commit `.env`.

---

# Logging

Use the centralized logging framework.

Do not use `print()` in production code.

---

# Error Handling

Raise meaningful custom exceptions.

Avoid catching broad exceptions unless they are logged and re-raised appropriately.

---

# Testing

Every new feature must include tests.

Prefer unit tests.

Add integration tests when external systems or the database are involved.

---

# Dependencies

Do not introduce new third-party libraries unless they provide clear long-term value.

Prefer the existing technology stack.

---

# Git

Use Conventional Commits.

Examples:

* feat(provider): add Yahoo Finance provider
* fix(database): resolve SQLite path issue
* refactor(service): simplify market data service
* test(provider): add provider tests

---

# Documentation

Update documentation whenever:

* architecture changes
* public APIs change
* repository structure changes
* configuration changes

---

# Performance

Avoid unnecessary loops.

Batch database writes where possible.

Avoid repeated API calls.

Design for future support of thousands of securities.

---

# Future Compatibility

Design code to support:

* Multiple market providers
* Multiple databases
* Multiple asset classes
* Async processing
* Parallel downloads

Avoid assumptions that limit future expansion.

---

# When Unsure

If requirements are ambiguous:

* Preserve existing architecture.
* Minimize changes.
* Request clarification rather than making assumptions.
