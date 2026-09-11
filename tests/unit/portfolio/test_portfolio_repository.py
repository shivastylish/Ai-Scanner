from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_screener.core.exceptions import ValidationError
from ai_screener.portfolio.repositories.portfolio_repository import (
    PortfolioRepository,
)

_NOW = datetime.now(UTC)


def test_record_buy_creates_a_new_holding(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 10, 100.0, _NOW)

    holding = portfolio_repository.get_holding("RELIANCE.NS")
    assert holding is not None
    assert holding.quantity == 10
    assert holding.average_cost == 100.0


def test_record_buy_updates_weighted_average_cost(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 10, 100.0, _NOW)
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 5, 130.0, _NOW)

    holding = portfolio_repository.get_holding("RELIANCE.NS")
    assert holding is not None
    assert holding.quantity == 15
    # (10*100 + 5*130) / 15 = 110
    assert holding.average_cost == pytest.approx(110.0)


def test_record_buy_rejects_non_positive_quantity(
    portfolio_repository: PortfolioRepository,
) -> None:
    with pytest.raises(ValidationError):
        portfolio_repository.record_buy("RELIANCE.NS", "equity", 0, 100.0, _NOW)


def test_record_sell_computes_realized_pnl_and_reduces_quantity(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 15, 110.0, _NOW)

    realized_pnl = portfolio_repository.record_sell(
        "RELIANCE.NS", "equity", 8, 150.0, _NOW
    )

    assert realized_pnl == pytest.approx(320.0)  # (150-110)*8

    holding = portfolio_repository.get_holding("RELIANCE.NS")
    assert holding is not None
    assert holding.quantity == pytest.approx(7.0)
    assert holding.average_cost == pytest.approx(110.0)  # unchanged on partial sell


def test_record_sell_that_fully_closes_removes_the_holding(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 10, 100.0, _NOW)

    portfolio_repository.record_sell("RELIANCE.NS", "equity", 10, 120.0, _NOW)

    assert portfolio_repository.get_holding("RELIANCE.NS") is None


def test_record_sell_more_than_held_raises(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 5, 100.0, _NOW)

    with pytest.raises(ValidationError):
        portfolio_repository.record_sell("RELIANCE.NS", "equity", 10, 120.0, _NOW)


def test_record_sell_with_no_holding_raises(
    portfolio_repository: PortfolioRepository,
) -> None:
    with pytest.raises(ValidationError):
        portfolio_repository.record_sell("RELIANCE.NS", "equity", 1, 100.0, _NOW)


def test_get_holdings_filters_by_asset_type(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 10, 100.0, _NOW)
    portfolio_repository.record_buy("SOMEFUND", "mutual_fund", 100, 10.0, _NOW)

    equity_holdings = portfolio_repository.get_holdings(asset_type="equity")

    assert [h.symbol for h in equity_holdings] == ["RELIANCE.NS"]
    assert len(portfolio_repository.get_holdings()) == 2


def test_get_transactions_records_every_buy_and_sell(
    portfolio_repository: PortfolioRepository,
) -> None:
    portfolio_repository.record_buy("RELIANCE.NS", "equity", 10, 100.0, _NOW)
    portfolio_repository.record_sell("RELIANCE.NS", "equity", 4, 120.0, _NOW)

    transactions = portfolio_repository.get_transactions("RELIANCE.NS")

    assert [t.transaction_type for t in transactions] == ["buy", "sell"]
    assert transactions[1].realized_pnl == pytest.approx(80.0)  # (120-100)*4
