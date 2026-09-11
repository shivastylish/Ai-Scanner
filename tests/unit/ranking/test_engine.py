from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_screener.ranking.engine import RankingEngine
from ai_screener.scanner.conditions.base import ConditionResult
from ai_screener.scanner.results import ScanResult


def _condition(
    name: str, value: float | None, threshold: float | None = None
) -> ConditionResult:
    return ConditionResult(
        condition_name=name,
        passed=value is not None,
        value=value,
        threshold=threshold,
        description="",
    )


def _scan_result(
    symbol: str, passed: bool, *condition_results: ConditionResult
) -> ScanResult:
    return ScanResult(
        symbol=symbol,
        passed=passed,
        condition_results=list(condition_results),
        scanned_at=datetime.now(UTC),
    )


def test_rank_excludes_symbols_that_did_not_pass_the_scan() -> None:
    passing = _scan_result("PASS.NS", True, _condition("narrow_cpr", 0.0, 0.5))
    failing = _scan_result("FAIL.NS", False, _condition("narrow_cpr", 2.0, 0.5))

    ranked = RankingEngine().rank([passing, failing])

    assert [r.symbol for r in ranked] == ["PASS.NS"]


def test_rank_orders_best_score_first() -> None:
    strong = _scan_result(
        "STRONG.NS",
        True,
        _condition("narrow_cpr", 0.0, 0.5),
        _condition("trend_above_ema", 105.0, 100.0),
        _condition("volume_above_average", 3000.0, 1000.0),
        _condition("momentum_positive", 75.0, 50.0),
    )
    weak = _scan_result(
        "WEAK.NS",
        True,
        _condition("narrow_cpr", None, 0.5),
        _condition("trend_above_ema", None, 100.0),
        _condition("volume_above_average", None, 1000.0),
        _condition("momentum_positive", None, 50.0),
    )

    ranked = RankingEngine().rank([weak, strong])

    assert [r.symbol for r in ranked] == ["STRONG.NS", "WEAK.NS"]
    assert ranked[0].score == pytest.approx(80.0)
    assert ranked[1].score == pytest.approx(0.0)


def test_confidence_reflects_evidence_completeness() -> None:
    full_evidence = _scan_result(
        "A.NS",
        True,
        _condition("narrow_cpr", 0.2, 0.5),
        _condition("trend_above_ema", 105.0, 100.0),
        _condition("volume_above_average", 1500.0, 1000.0),
        _condition("momentum_positive", 60.0, 50.0),
    )
    partial_evidence = _scan_result(
        "B.NS",
        True,
        _condition("narrow_cpr", 0.2, 0.5),
        _condition("trend_above_ema", None, 100.0),
        _condition("volume_above_average", None, 1000.0),
        _condition("momentum_positive", 60.0, 50.0),
    )

    ranked = {
        r.symbol: r for r in RankingEngine().rank([full_evidence, partial_evidence])
    }

    assert ranked["A.NS"].confidence == pytest.approx(100.0)
    assert ranked["B.NS"].confidence == pytest.approx(50.0)


def test_confidence_is_zero_with_no_condition_results() -> None:
    result = _scan_result("A.NS", True)

    ranked = RankingEngine().rank([result])

    assert ranked[0].confidence == 0.0
    assert ranked[0].score == 0.0
