from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.market_data.services import MarketDataService
from ai_screener.scanner.conditions.base import ConditionResult
from ai_screener.scanner.engine import ScannerEngine
from ai_screener.scanner.repositories.scan_result_repository import (
    ScanResultRepository,
)
from ai_screener.scanner.results import ScanResult
from ai_screener.scanner.rules import build_strategy

_MOMENTUM_ONLY_STRATEGY = {
    "name": "momentum_only",
    "conditions": [
        {"type": "momentum_positive", "params": {"rsi_threshold": 50.0}},
    ],
}


def test_scan_persists_a_result_per_symbol(
    service: MarketDataService,
    scanner_engine: ScannerEngine,
    scan_repository: ScanResultRepository,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    strategy = build_strategy(_MOMENTUM_ONLY_STRATEGY)
    results = scanner_engine.scan(universe=["RELIANCE.NS"], strategy=strategy)

    assert len(results) == 1
    assert results[0].symbol == "RELIANCE.NS"
    assert len(results[0].condition_results) == 1
    assert results[0].condition_results[0].condition_name == "momentum_positive"

    # Only 5 fake daily bars exist - not enough for RSI(14) - so the
    # condition should fail gracefully rather than pass on missing data.
    assert results[0].passed is False

    persisted = scan_repository.get_latest_run_results("momentum_only")
    assert len(persisted) == 1
    assert persisted[0].symbol == "RELIANCE.NS"
    assert persisted[0].condition_results[0].condition_name == "momentum_positive"


def test_scan_skips_symbols_with_no_persisted_data(
    scanner_engine: ScannerEngine,
) -> None:
    strategy = build_strategy(_MOMENTUM_ONLY_STRATEGY)

    results = scanner_engine.scan(universe=["UNKNOWN.NS"], strategy=strategy)

    assert results == []


def test_scan_does_not_persist_when_persist_is_false(
    service: MarketDataService,
    scanner_engine: ScannerEngine,
    scan_repository: ScanResultRepository,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")
    strategy = build_strategy(_MOMENTUM_ONLY_STRATEGY)

    scanner_engine.scan(universe=["RELIANCE.NS"], strategy=strategy, persist=False)

    assert scan_repository.get_latest_run_results("momentum_only") == []


def test_get_passed_symbols_filters_to_passing_results(
    scan_repository: ScanResultRepository,
) -> None:
    now = datetime.now(UTC)
    results = [
        ScanResult(
            symbol="RELIANCE.NS",
            passed=True,
            condition_results=[
                ConditionResult(
                    condition_name="stub",
                    passed=True,
                    value=1,
                    threshold=0,
                    description="stub",
                )
            ],
            scanned_at=now,
        ),
        ScanResult(
            symbol="TCS.NS",
            passed=False,
            condition_results=[
                ConditionResult(
                    condition_name="stub",
                    passed=False,
                    value=0,
                    threshold=1,
                    description="stub",
                )
            ],
            scanned_at=now,
        ),
    ]

    scan_repository.save_scan(
        strategy_name="mixed_results", asset_type="equity", results=results
    )

    assert scan_repository.get_passed_symbols("mixed_results") == ["RELIANCE.NS"]
