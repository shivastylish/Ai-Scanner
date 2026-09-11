from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.backtesting.db_models import BacktestRun, BacktestTrade
from ai_screener.backtesting.metrics import BacktestMetrics
from ai_screener.backtesting.results import BacktestResult
from ai_screener.backtesting.simulator import Trade
from ai_screener.database.session import SessionLocal, engine, initialize_database


class BacktestRepository:
    """Persistence adapter for backtest runs and their simulated trades."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def save(self, result: BacktestResult) -> int:
        """Persist a completed backtest run and its trades.

        Only closed trades (with a pnl) are persisted; an engine bug
        that left a trade open would otherwise silently vanish here
        instead of surfacing.
        """

        with self._session_factory() as session:
            run = BacktestRun(
                strategy_name=result.strategy_name,
                asset_type=result.asset_type,
                start_date=result.start_date,
                end_date=result.end_date,
                total_trades=result.metrics.total_trades,
                win_rate_pct=result.metrics.win_rate_pct,
                average_return_pct=result.metrics.average_return_pct,
                total_pnl=result.metrics.total_pnl,
                max_drawdown_pct=result.metrics.max_drawdown_pct,
                run_at=datetime.now(UTC),
            )
            session.add(run)
            session.flush()

            trade_records = [
                BacktestTrade(
                    backtest_run_id=run.id,
                    symbol=trade.symbol,
                    entry_date=trade.entry_date,
                    entry_price=trade.entry_price,
                    quantity=trade.quantity,
                    exit_date=trade.exit_date,
                    exit_price=trade.exit_price,
                    exit_reason=trade.exit_reason,
                    pnl=trade.pnl,
                    return_pct=trade.return_pct,
                )
                for trade in result.trades
                if trade.pnl is not None
            ]
            session.add_all(trade_records)
            session.commit()

            return run.id

    def get_latest(
        self, strategy_name: str, asset_type: str = "equity"
    ) -> BacktestResult | None:
        """Return the most recent backtest run for a strategy, if any."""

        with self._session_factory() as session:
            run = session.execute(
                select(BacktestRun)
                .where(
                    BacktestRun.strategy_name == strategy_name,
                    BacktestRun.asset_type == asset_type,
                )
                .order_by(BacktestRun.run_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if run is None:
                return None

            trade_records = (
                session.execute(
                    select(BacktestTrade).where(BacktestTrade.backtest_run_id == run.id)
                )
                .scalars()
                .all()
            )

            trades = [
                Trade(
                    symbol=t.symbol,
                    entry_date=t.entry_date,
                    entry_price=t.entry_price,
                    quantity=t.quantity,
                    exit_date=t.exit_date,
                    exit_price=t.exit_price,
                    exit_reason=t.exit_reason,
                    pnl=t.pnl,
                    return_pct=t.return_pct,
                )
                for t in trade_records
            ]

            return BacktestResult(
                strategy_name=run.strategy_name,
                asset_type=run.asset_type,
                start_date=run.start_date,
                end_date=run.end_date,
                trades=trades,
                metrics=BacktestMetrics(
                    total_trades=run.total_trades,
                    win_rate_pct=run.win_rate_pct,
                    average_return_pct=run.average_return_pct,
                    total_pnl=run.total_pnl,
                    max_drawdown_pct=run.max_drawdown_pct,
                ),
            )
