# AI Screener – Project Charter

**Document ID:** DOC-001
**Version:** 0.1.0-alpha
**Project ID:** AIS
**Project Name:** AI Screener
**Sprint:** Sprint 0 – Foundation
**Status:** Approved
**Created On:** 05-Aug-2026

---

# 1. Vision

To build the most trusted AI-powered stock research platform for Indian equity markets by combining quantitative analysis, explainable AI, disciplined engineering, and rigorous validation.

AI Screener is a **decision-support platform**, not a prediction engine.

---

# 2. Mission

Help traders and investors make informed decisions through transparent analysis, historical validation, disciplined risk management, and continuous learning.

---

# 3. Product Philosophy

AI Screener exists to answer five questions for every recommendation:

* Why was this stock selected?
* What evidence supports the recommendation?
* What are the risks?
* What could invalidate the setup?
* How have similar setups performed historically?

If the platform cannot answer these questions, the recommendation is not ready.

---

# 4. Core Principles

## 4.1 Evidence First

All strategies must be supported by historical testing.

## 4.2 Explainability First

Every recommendation must include a clear explanation.

## 4.3 Risk First

Capital preservation is more important than maximizing returns.

## 4.4 Architecture First

Design before implementation.

## 4.5 Quality First

Every module must be documented, tested, and reviewed.

---

# 5. Objectives

## Short-Term Objectives

* Build a reliable market data engine.
* Implement accurate CPR calculations.
* Scan all NSE-listed stocks.
* Generate explainable recommendations.
* Export professional reports.

## Long-Term Objectives

* AI-assisted ranking engine.
* Strategy laboratory.
* Historical backtesting framework.
* Portfolio analytics.
* Trading journal.
* Market intelligence dashboard.
* Mobile and web applications.

---

# 6. Scope

## Included in Version 1.0

* Market Data Engine
* CPR Engine
* Scanner Engine
* Ranking Engine
* Explainability Engine
* Backtesting
* Desktop Application
* Trade Journal

## Excluded from Version 1.0

* Automated trade execution
* Broker integration
* Social/community features
* Mobile applications
* Advanced AI prediction models

---

# 7. Stakeholders

## Founder / Product Owner

Responsibilities:

* Product vision
* Feature prioritization
* Trading validation
* Acceptance testing

## Solution Architect

Responsibilities:

* Architecture
* Engineering standards
* Technical design
* Documentation
* Code quality

---

# 8. Success Criteria

AI Screener is successful when:

* Market data is accurate and reliable.
* CPR calculations match trusted references.
* Every recommendation is explainable.
* Strategies are validated before use.
* Architecture remains modular.
* Documentation stays synchronized with implementation.

---

# 9. Engineering Principles

Every module must satisfy the following before completion:

* Requirements documented
* Design completed
* Implementation completed
* Unit tests passing
* Documentation updated
* Code reviewed
* Acceptance criteria met

---

# 10. Project Modules

* Foundation
* Market Data Engine
* Indicator Engine
* Scanner Engine
* Ranking Engine
* Explainability Engine
* Backtesting Engine
* Desktop Dashboard
* Portfolio Module
* Trade Journal
* AI Engine
* Alerts
* Market Intelligence

---

# 11. Development Methodology

Development follows Agile sprints.

Every feature progresses through:

Requirements → Design → Development → Testing → Documentation → Review → Release

No phase is skipped.

---

# 12. Git Strategy

Main Branch

Stable releases only.

Develop Branch

Integration branch.

Feature Branches

One feature or module per branch.

Example:

* feature/project-foundation
* feature/market-data
* feature/cpr-engine
* feature/scanner

---

# 13. Documentation Policy

Documentation is treated as part of the product.

Every module must include:

* README
* Design
* Test Cases
* Change Log

---

# 14. Versioning

Version format:

Major.Minor.Patch

Examples:

* v0.1.0 Foundation
* v0.2.0 Market Data
* v0.3.0 Indicator Engine
* v1.0.0 Beta

---

# 15. Risk Management Philosophy

The platform will never guarantee profits.

Instead, it will:

* Identify opportunities
* Highlight risks
* Present evidence
* Support informed decision-making

The final trading decision always belongs to the user.

---

# 16. Definition of Done

A module is complete only when:

* Requirements are implemented.
* Tests pass.
* Documentation is updated.
* Review is complete.
* Acceptance criteria are satisfied.
* Git history is clean.

---

# 17. Project Motto

**Build with Evidence. Validate with Data. Earn Trust.**

---

# 18. Charter Approval

This Project Charter serves as the governing document for AI Screener Version 1.0.

Any significant architectural or product changes should be reviewed against the principles defined in this charter before implementation.
