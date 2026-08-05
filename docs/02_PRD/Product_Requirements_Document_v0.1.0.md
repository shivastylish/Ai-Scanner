# AI Screener – Product Requirements Document (PRD)

**Document ID:** DOC-002
**Version:** 0.1.0-alpha
**Project:** AI Screener
**Sprint:** Sprint 0
**Status:** Draft v1

---

# Revision History

| Version | Date        | Description         |
| ------- | ----------- | ------------------- |
| 0.1.0   | 05-Aug-2026 | Initial PRD created |

---

# 1. Executive Summary

AI Screener is an AI-powered stock research platform for the Indian equity market.

Its purpose is to help traders and investors make informed decisions by combining technical analysis, quantitative research, explainable recommendations, and disciplined risk management.

The platform is designed as a decision-support system. It does not guarantee outcomes or automate trading decisions.

---

# 2. Problem Statement

Current stock screeners generally:

* Return long lists of stocks without prioritization.
* Provide little or no explanation for recommendations.
* Rarely validate strategies with historical evidence.
* Focus on indicators instead of decision quality.
* Do not integrate research, risk, and explainability into one workflow.

AI Screener aims to address these limitations.

---

# 3. Vision

Build the most trusted AI-powered stock research platform for Indian equities.

---

# 4. Goals

## Business Goals

* Deliver reliable market analysis.
* Build user trust through transparency.
* Create a scalable research platform.

## Product Goals

* Scan the Indian market.
* Rank opportunities.
* Explain recommendations.
* Support historical validation.
* Maintain modular architecture.

---

# 5. Target Users

### Primary Users

* Swing traders
* Positional traders
* Technical analysts

### Future Users

* Investors
* Research analysts
* Portfolio managers

---

# 6. Version 1 Scope

### Included

* Market Data Engine
* CPR Engine
* Scanner
* Ranking
* Explainability
* Desktop Application
* Backtesting
* Portfolio Tracker
* Trade Journal

### Excluded

* Live trade execution
* Broker APIs
* Mobile apps
* Social/community features
* Paid subscriptions

---

# 7. Functional Requirements

## FR-001 Market Data

The system shall:

* Download NSE symbols.
* Download historical OHLCV data.
* Update data incrementally.
* Validate downloaded data.

---

## FR-002 Indicator Engine

The system shall calculate:

* Daily CPR
* Weekly CPR
* Monthly CPR
* CPR Width
* Virgin CPR
* CPR Relationships
* EMA
* RSI
* ATR
* MACD

---

## FR-003 Scanner

The scanner shall:

* Scan all configured stocks.
* Apply configurable filters.
* Generate ranked candidates.
* Export reports.

---

## FR-004 Ranking Engine

The ranking engine shall:

* Assign configurable scores.
* Support weighted scoring.
* Produce ranked watchlists.

---

## FR-005 Explainability Engine

Every recommendation shall include:

* Why selected
* Why not selected
* Contributing factors
* Risk factors
* Confidence level
* Historical evidence (when available)

---

## FR-006 Backtesting

The system shall:

* Execute historical strategy tests.
* Calculate performance metrics.
* Compare strategy variations.

---

## FR-007 Portfolio

The system shall:

* Track holdings.
* Calculate P&L.
* Measure exposure.
* Display portfolio statistics.

---

## FR-008 Trade Journal

Users shall be able to record:

* Entry
* Exit
* Notes
* Trade rationale
* Lessons learned

---

# 8. Non-Functional Requirements

## Performance

* Complete market scan within the target time budget established during implementation.
* Support incremental data updates.

## Reliability

* Gracefully handle missing or incomplete data.
* Log all critical failures.

## Scalability

Architecture must support:

* Additional indicators
* New scanners
* New exchanges
* AI modules

## Maintainability

* Modular design
* Type hints
* Documentation
* Unit testing

---

# 9. User Experience Requirements

The application should provide:

* Clean dashboard
* Simple navigation
* Explainable recommendations
* Fast search
* Responsive charts

---

# 10. Security

* Configuration separated from code.
* No credentials stored in source files.
* Secure handling of future API keys.

---

# 11. Success Metrics

Version 1 succeeds if:

* CPR calculations match trusted references.
* Scanner produces reproducible results.
* Recommendations are explainable.
* Historical validation framework is operational.
* Documentation remains synchronized with implementation.

---

# 12. Risks

* Data quality issues
* Strategy overfitting
* Performance bottlenecks
* Feature creep
* Documentation drift

---

# 13. Assumptions

* Reliable market data is available.
* Users make final trading decisions.
* Strategies require continuous validation.

---

# 14. Dependencies

Sprint 1 depends on:

* Project Charter
* Repository setup
* Coding standards
* HLD
* LLD

---

# 15. Acceptance Criteria

This PRD is accepted when:

* Product scope is clearly defined.
* Functional requirements are documented.
* Non-functional requirements are documented.
* Version 1 boundaries are established.
* Engineering can begin HLD without ambiguity.

---

# 16. Next Document

**DOC-003 — High-Level Design (HLD)**

This document will translate these requirements into system architecture, module interactions, technology choices, and data flow diagrams.
