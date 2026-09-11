from __future__ import annotations

import pytest

from ai_screener.market_data.services import MarketDataService
from ai_screener.portfolio.service import PortfolioService


def test_buy_and_sell_delegate_to_the_repository(
    portfolio_service: PortfolioService,
) -> None:
    portfolio_service.buy("RELIANCE.NS", 10, 100.0)

    valuations = portfolio_service.get_valuations()
    assert len(valuations) == 1
    assert valuations[0].quantity == 10

    realized_pnl = portfolio_service.sell("RELIANCE.NS", 4, 120.0)
    assert realized_pnl == pytest.approx(80.0)


def test_get_valuations_prices_holdings_against_latest_close(
    service: MarketDataService,
    portfolio_service: PortfolioService,
) -> None:
    # FakeEquityProvider's 5th (last) fake day: base=104, close=106.
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")
    portfolio_service.buy("RELIANCE.NS", 10, 100.0)

    valuations = portfolio_service.get_valuations()

    assert len(valuations) == 1
    valuation = valuations[0]
    assert valuation.current_price == pytest.approx(106.0)
    assert valuation.market_value == pytest.approx(1060.0)
    assert valuation.unrealized_pnl == pytest.approx(60.0)
    assert valuation.unrealized_pnl_pct == pytest.approx(6.0)


def test_get_valuations_handles_symbols_with_no_market_data(
    portfolio_service: PortfolioService,
) -> None:
    portfolio_service.buy("UNKNOWN.NS", 10, 100.0)

    valuations = portfolio_service.get_valuations()

    assert valuations[0].current_price is None
    assert valuations[0].market_value is None
    assert valuations[0].unrealized_pnl is None


def test_get_total_exposure_sums_market_values(
    service: MarketDataService,
    portfolio_service: PortfolioService,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")
    portfolio_service.buy("RELIANCE.NS", 10, 100.0)
    portfolio_service.buy("UNKNOWN.NS", 5, 50.0)  # no market data -> excluded

    assert portfolio_service.get_total_exposure() == pytest.approx(1060.0)


def test_get_realized_pnl_sums_across_sells(
    portfolio_service: PortfolioService,
) -> None:
    portfolio_service.buy("RELIANCE.NS", 10, 100.0)
    portfolio_service.sell("RELIANCE.NS", 4, 120.0)
    portfolio_service.sell("RELIANCE.NS", 6, 90.0)

    # (120-100)*4 + (90-100)*6 = 80 - 60 = 20
    assert portfolio_service.get_realized_pnl() == pytest.approx(20.0)
    assert portfolio_service.get_realized_pnl(symbol="RELIANCE.NS") == pytest.approx(
        20.0
    )
