from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.explainability.repositories.explanation_repository import (
    ExplanationRepository,
)
from ai_screener.explainability.service import ExplainabilityService
from ai_screener.scanner.conditions.base import ConditionResult
from ai_screener.scanner.results import ScanResult


def _scan_result(*condition_results: ConditionResult) -> ScanResult:
    return ScanResult(
        symbol="RELIANCE.NS",
        passed=True,
        condition_results=list(condition_results),
        scanned_at=datetime.now(UTC),
    )


def test_explain_collects_reasons_from_every_builder_with_evidence(
    explainability_service: ExplainabilityService,
) -> None:
    scan_result = _scan_result(
        ConditionResult("narrow_cpr", True, 0.3, 0.5, "narrow"),
        ConditionResult("trend_above_ema", True, 110.0, 100.0, "above"),
        ConditionResult("volume_above_average", True, 3000.0, 1000.0, "high"),
        ConditionResult("momentum_positive", True, 65.0, 50.0, "bullish"),
    )

    explanation = explainability_service.explain(scan_result)

    categories = {reason.category for reason in explanation.reasons}
    # cpr, trend, volume, momentum, and risk (reusing the CPR evidence) -
    # historical_performance is deliberately absent until Sprint 6.
    assert categories == {"cpr", "trend", "volume", "momentum", "risk"}


def test_explain_skips_builders_with_no_evidence(
    explainability_service: ExplainabilityService,
) -> None:
    scan_result = _scan_result(
        ConditionResult("momentum_positive", True, 65.0, 50.0, "bullish")
    )

    explanation = explainability_service.explain(scan_result)

    categories = {reason.category for reason in explanation.reasons}
    assert categories == {"momentum"}


def test_explain_persists_by_default(
    explainability_service: ExplainabilityService,
    explanation_repository: ExplanationRepository,
) -> None:
    scan_result = _scan_result(ConditionResult("narrow_cpr", True, 0.3, 0.5, "narrow"))

    explainability_service.explain(scan_result)

    persisted = explanation_repository.get_latest("RELIANCE.NS")
    assert persisted is not None
    assert persisted.symbol == "RELIANCE.NS"
    assert len(persisted.reasons) >= 1


def test_explain_does_not_persist_when_persist_is_false(
    explainability_service: ExplainabilityService,
    explanation_repository: ExplanationRepository,
) -> None:
    scan_result = _scan_result(ConditionResult("narrow_cpr", True, 0.3, 0.5, "narrow"))

    explainability_service.explain(scan_result, persist=False)

    assert explanation_repository.get_latest("RELIANCE.NS") is None


def test_explain_uses_scan_result_evidence_completeness_when_no_ranked_result(
    explainability_service: ExplainabilityService,
) -> None:
    scan_result = _scan_result(
        ConditionResult("narrow_cpr", True, 0.3, 0.5, "narrow"),
        ConditionResult("trend_above_ema", False, None, 100.0, "no data"),
    )

    explanation = explainability_service.explain(scan_result)

    assert explanation.confidence == 50.0


def test_get_latest_returns_none_for_unknown_symbol(
    explanation_repository: ExplanationRepository,
) -> None:
    assert explanation_repository.get_latest("UNKNOWN.NS") is None
