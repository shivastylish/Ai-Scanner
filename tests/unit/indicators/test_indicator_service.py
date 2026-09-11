from __future__ import annotations

from ai_screener.indicators.bootstrap import register_default_indicators
from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.services import MarketDataService


def test_compute_returns_default_indicator_columns(
    service: MarketDataService,
) -> None:
    register_default_indicators()

    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    indicator_service = IndicatorService(market_data_service=service)

    snapshot = indicator_service.compute(symbol="RELIANCE.NS")

    assert not snapshot.empty
    for expected_column in (
        "cpr_daily_pivot",
        "cpr_weekly_pivot",
        "cpr_monthly_pivot",
        "ema_ema_20",
        "rsi_rsi_14",
        "atr_atr_14",
        "macd_macd_line",
    ):
        assert expected_column in snapshot.columns


def test_latest_returns_most_recent_row_as_dict(
    service: MarketDataService,
) -> None:
    register_default_indicators()

    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    indicator_service = IndicatorService(market_data_service=service)

    latest = indicator_service.latest(symbol="RELIANCE.NS")

    assert "datetime" in latest


def test_latest_returns_empty_dict_for_unknown_symbol(
    service: MarketDataService,
) -> None:
    register_default_indicators()

    indicator_service = IndicatorService(market_data_service=service)

    assert indicator_service.latest(symbol="UNKNOWN.NS") == {}
