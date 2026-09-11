from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.market_data.services import MarketDataService
from ai_screener.portfolio.models import Holding, HoldingValuation
from ai_screener.portfolio.repositories.portfolio_repository import (
    PortfolioRepository,
)


class PortfolioService:
    """Orchestrates portfolio bookkeeping (via PortfolioRepository) and
    live valuation (via MarketDataService's read path - never a
    repository directly)."""

    def __init__(
        self,
        repository: PortfolioRepository | None = None,
        market_data_service: MarketDataService | None = None,
    ) -> None:
        self._repository = repository or PortfolioRepository()
        self._market_data_service = market_data_service or MarketDataService()

    def buy(
        self,
        symbol: str,
        quantity: float,
        price: float,
        asset_type: str = "equity",
        transacted_at: datetime | None = None,
    ) -> None:
        self._repository.record_buy(
            symbol, asset_type, quantity, price, transacted_at or datetime.now(UTC)
        )

    def sell(
        self,
        symbol: str,
        quantity: float,
        price: float,
        asset_type: str = "equity",
        transacted_at: datetime | None = None,
    ) -> float:
        """Returns the realized P&L for this sell."""

        return self._repository.record_sell(
            symbol, asset_type, quantity, price, transacted_at or datetime.now(UTC)
        )

    def get_valuations(self, asset_type: str = "equity") -> list[HoldingValuation]:
        """Price every current holding against the latest persisted bar."""

        return [
            self._value_holding(holding)
            for holding in self._repository.get_holdings(asset_type)
        ]

    def get_total_exposure(self, asset_type: str = "equity") -> float:
        return sum(
            valuation.market_value or 0.0
            for valuation in self.get_valuations(asset_type)
        )

    def get_realized_pnl(self, symbol: str | None = None) -> float:
        return sum(
            transaction.realized_pnl or 0.0
            for transaction in self._repository.get_transactions(symbol)
        )

    def _value_holding(self, holding: Holding) -> HoldingValuation:
        history = self._market_data_service.get_history(
            holding.symbol, holding.asset_type
        )

        current_price = None if history.empty else float(history["close"].iloc[-1])

        market_value = (
            None if current_price is None else current_price * holding.quantity
        )
        unrealized_pnl = (
            None
            if current_price is None
            else (current_price - holding.average_cost) * holding.quantity
        )
        unrealized_pnl_pct = (
            None
            if current_price is None or not holding.average_cost
            else (current_price - holding.average_cost) / holding.average_cost * 100
        )

        return HoldingValuation(
            symbol=holding.symbol,
            asset_type=holding.asset_type,
            quantity=holding.quantity,
            average_cost=holding.average_cost,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct,
        )
