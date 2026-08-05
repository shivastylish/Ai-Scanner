# AI Screener – High-Level Design (HLD)

**Document ID:** DOC-003
**Version:** 0.1.0-alpha
**Sprint:** Sprint 0
**Status:** Draft

---

# 1. Purpose

This document defines the overall architecture of AI Screener, the major system modules, and how they interact.

It intentionally avoids implementation details. Those will be covered in the Low-Level Design (LLD).

---

# 2. Architecture Goals

* Modular and maintainable
* Easily testable
* Scalable
* Explainable
* Configuration-driven
* Platform independent

---

# 3. Architectural Principles

* Single Responsibility Principle
* Low Coupling
* High Cohesion
* Separation of Concerns
* Clean Architecture
* Testability First

---

# 4. System Overview

```text
+--------------------------------------------------+
|              Desktop Application                 |
|            (PySide6 / Future Web UI)             |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|            Application Service Layer             |
+--------------------------------------------------+
| Scanner | Ranking | Explainability | Portfolio   |
+--------------------------------------------------+
                          |
                          v
+--------------------------------------------------+
|                  Domain Layer                    |
+--------------------------------------------------+
| CPR | Indicators | Strategies | Backtesting      |
+--------------------------------------------------+
                          |
                          v
+--------------------------------------------------+
|              Infrastructure Layer                |
+--------------------------------------------------+
| Data Downloader | Database | Logging | Config    |
+--------------------------------------------------+
```

---

# 5. Major Modules

## Foundation

Project configuration, logging, constants, utilities and dependency management.

## Market Data Engine

Responsible for downloading, validating and maintaining historical market data.

## Indicator Engine

Calculates all supported indicators including Daily, Weekly and Monthly CPR.

## Scanner Engine

Scans configured stocks using configurable screening rules.

## Ranking Engine

Produces a weighted score based on technical and research criteria.

## Explainability Engine

Generates human-readable explanations for every recommendation.

## Backtesting Engine

Evaluates historical performance of strategies.

## Portfolio Module

Tracks positions and portfolio analytics.

## Trade Journal

Stores trade notes and learning history.

## Dashboard

Displays reports, watchlists and analytics.

---

# 6. Data Flow

1. Download market data.
2. Store validated data.
3. Calculate indicators.
4. Execute scanner.
5. Rank results.
6. Generate explanations.
7. Present results to the user.
8. Record portfolio and journal information.

---

# 7. Technology Stack

## Language

Python 3.12+

## Desktop UI

PySide6

## Database

SQLite (initially), PostgreSQL (future)

## Data Processing

Pandas
NumPy

## Charts

TradingView Lightweight Charts (future integration)

## Testing

pytest

## Version Control

Git + GitHub

---

# 8. Security Principles

* No secrets committed to Git.
* Configuration stored separately.
* Input validation for all external data.
* Structured logging without sensitive information.

---

# 9. Scalability Strategy

The architecture supports future addition of:

* New indicators
* New exchanges
* AI models
* Web application
* Mobile application
* Broker integrations

without requiring major redesign.

---

# 10. Module Dependencies

Foundation → Market Data → Indicator Engine → Scanner → Ranking → Explainability → Dashboard

Backtesting, Portfolio and Trade Journal consume outputs from the earlier modules but remain independent.

---

# 11. Non-Functional Targets

* Reliable data ingestion
* Maintainable codebase
* Fast incremental updates
* Comprehensive documentation
* High unit test coverage

---

# 12. Next Document

**DOC-004 – Foundation Low-Level Design (LLD)**

This document will define folder structure, package layout, interfaces, naming conventions, and responsibilities for each component.
