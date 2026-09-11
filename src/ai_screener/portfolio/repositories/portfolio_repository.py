from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.core.exceptions import ValidationError
from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.portfolio.db_models import HoldingRecord, TransactionRecord
from ai_screener.portfolio.models import Holding, Transaction

_QUANTITY_EPSILON = 1e-9


class PortfolioRepository:
    """Persistence adapter for holdings and the transactions behind them.

    Owns the weighted-average-cost and realized-P&L arithmetic (it's
    pure bookkeeping over storage, not the kind of cross-cutting business
    logic PortfolioService is for) - PortfolioService adds live
    valuation on top of what this repository already tracks.
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def record_buy(
        self,
        symbol: str,
        asset_type: str,
        quantity: float,
        price: float,
        transacted_at: datetime,
    ) -> None:
        if quantity <= 0:
            raise ValidationError("Buy quantity must be positive.")

        with self._session_factory() as session:
            record = self._get_holding_record(session, symbol, asset_type)

            if record is None:
                record = HoldingRecord(
                    symbol=symbol,
                    asset_type=asset_type,
                    quantity=quantity,
                    average_cost=price,
                    opened_at=transacted_at,
                    updated_at=transacted_at,
                )
                session.add(record)
            else:
                total_cost = record.quantity * record.average_cost + quantity * price
                new_quantity = record.quantity + quantity
                record.quantity = new_quantity
                record.average_cost = total_cost / new_quantity
                record.updated_at = transacted_at

            session.add(
                TransactionRecord(
                    symbol=symbol,
                    asset_type=asset_type,
                    transaction_type="buy",
                    quantity=quantity,
                    price=price,
                    realized_pnl=None,
                    transacted_at=transacted_at,
                )
            )
            session.commit()

    def record_sell(
        self,
        symbol: str,
        asset_type: str,
        quantity: float,
        price: float,
        transacted_at: datetime,
    ) -> float:
        """Record a sell. Returns the realized P&L for this transaction."""

        if quantity <= 0:
            raise ValidationError("Sell quantity must be positive.")

        with self._session_factory() as session:
            record = self._get_holding_record(session, symbol, asset_type)

            if record is None or quantity > record.quantity + _QUANTITY_EPSILON:
                held = 0.0 if record is None else record.quantity
                raise ValidationError(
                    f"Cannot sell {quantity} of '{symbol}': only {held} held."
                )

            realized_pnl = (price - record.average_cost) * quantity
            remaining = record.quantity - quantity

            if remaining <= _QUANTITY_EPSILON:
                session.delete(record)
            else:
                record.quantity = remaining
                record.updated_at = transacted_at

            session.add(
                TransactionRecord(
                    symbol=symbol,
                    asset_type=asset_type,
                    transaction_type="sell",
                    quantity=quantity,
                    price=price,
                    realized_pnl=realized_pnl,
                    transacted_at=transacted_at,
                )
            )
            session.commit()

            return realized_pnl

    def get_holdings(self, asset_type: str | None = None) -> list[Holding]:
        with self._session_factory() as session:
            statement = select(HoldingRecord)
            if asset_type is not None:
                statement = statement.where(HoldingRecord.asset_type == asset_type)
            records = session.execute(statement).scalars().all()
            return [_to_holding(record) for record in records]

    def get_holding(self, symbol: str, asset_type: str = "equity") -> Holding | None:
        with self._session_factory() as session:
            record = self._get_holding_record(session, symbol, asset_type)
            return None if record is None else _to_holding(record)

    def get_transactions(self, symbol: str | None = None) -> list[Transaction]:
        with self._session_factory() as session:
            statement = select(TransactionRecord).order_by(
                TransactionRecord.transacted_at.asc()
            )
            if symbol is not None:
                statement = statement.where(TransactionRecord.symbol == symbol)
            records = session.execute(statement).scalars().all()
            return [_to_transaction(record) for record in records]

    @staticmethod
    def _get_holding_record(
        session: Session, symbol: str, asset_type: str
    ) -> HoldingRecord | None:
        statement = select(HoldingRecord).where(
            HoldingRecord.symbol == symbol, HoldingRecord.asset_type == asset_type
        )
        return session.execute(statement).scalar_one_or_none()


def _to_holding(record: HoldingRecord) -> Holding:
    return Holding(
        symbol=record.symbol,
        asset_type=record.asset_type,
        quantity=record.quantity,
        average_cost=record.average_cost,
        opened_at=record.opened_at,
        updated_at=record.updated_at,
    )


def _to_transaction(record: TransactionRecord) -> Transaction:
    return Transaction(
        symbol=record.symbol,
        asset_type=record.asset_type,
        transaction_type=record.transaction_type,
        quantity=record.quantity,
        price=record.price,
        realized_pnl=record.realized_pnl,
        transacted_at=record.transacted_at,
    )
