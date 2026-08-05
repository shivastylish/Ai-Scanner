# AI Screener – Architecture Decision Records (ADR)

**Document ID:** DOC-008

**Version:** 0.1.0-alpha

**Status:** Approved

---

# Purpose

Architecture Decision Records (ADRs) capture important technical decisions made during the development of AI Screener.

Every major architectural decision should be documented here so future contributors understand **what was decided, why it was decided, and what alternatives were considered.**

---

# ADR-001

## Title

Use Python as the Primary Programming Language

### Status

Accepted

### Decision

AI Screener will be developed primarily in Python.

### Rationale

* Excellent data analysis ecosystem
* Mature AI/ML libraries
* Strong community support
* Easy integration with financial data processing

### Alternatives Considered

* Java
* C#
* Node.js

---

# ADR-002

## Title

Adopt Modular Clean Architecture

### Status

Accepted

### Decision

The application will be organized into independent modules with clear responsibilities.

### Rationale

* Easier maintenance
* Better testing
* Lower coupling
* Higher scalability

### Alternatives Considered

* Monolithic design
* Layered architecture without module boundaries

---

# ADR-003

## Title

Desktop Application First

### Status

Accepted

### Decision

The first production release targets Windows desktop.

### Rationale

* Faster development
* Easier debugging
* Better performance for research workflows
* Single codebase before expanding to web/mobile

### Future Direction

Web and mobile clients will reuse the same backend architecture where practical.

---

# ADR-004

## Title

Explainability Before AI

### Status

Accepted

### Decision

Every recommendation must include an explanation.

### Rationale

User trust depends on understanding **why** a recommendation exists.

A score without evidence is not sufficient.

---

# ADR-005

## Title

Backtesting Before Strategy Release

### Status

Accepted

### Decision

No strategy becomes part of AI Screener until it has been historically validated.

### Rationale

Historical testing reduces reliance on assumptions and helps identify weaknesses before live use.

---

# ADR-006

## Title

Documentation is a Deliverable

### Status

Accepted

### Decision

Documentation must be updated alongside implementation.

### Rationale

Documentation is part of the product, not an afterthought.

---

# ADR-007

## Title

One Module Per Feature Branch

### Status

Accepted

### Decision

Each functional module (Sprint 1 onward) will use its own feature branch.

### Exception

Sprint 0 uses:

feature/project-foundation

---

# ADR-008

## Title

Configuration Over Hard-Coding

### Status

Accepted

### Decision

Configurable values must reside in configuration files or environment variables.

### Rationale

Improves flexibility, maintainability, and deployment consistency.

---

# ADR-009

## Title

Data Quality Takes Priority

### Status

Accepted

### Decision

Reliable market data is more important than adding new indicators quickly.

### Rationale

Incorrect data affects every downstream calculation and recommendation.

---

# ADR-010

## Title

AI Assists, Users Decide

### Status

Accepted

### Decision

AI Screener provides research and decision support.

The user always makes the final trading decision.

### Rationale

The platform is designed to improve decision quality, not replace user judgment.

---

# ADR Lifecycle

Every new ADR follows this process:

Proposed

↓

Reviewed

↓

Accepted / Rejected

↓

Implemented

↓

Archived (if superseded)

---

# ADR Template

Every future ADR should contain:

* ADR Number
* Title
* Status
* Context
* Decision
* Rationale
* Alternatives Considered
* Consequences
* Future Review (if applicable)

---

# Guiding Principle

Architectural decisions should be intentional, documented, and easy to revisit when requirements evolve.
