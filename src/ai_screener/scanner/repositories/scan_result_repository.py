from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.scanner.conditions.base import ConditionResult
from ai_screener.scanner.models import ScanResultRecord, ScanRun
from ai_screener.scanner.results import ScanResult


class ScanResultRepository:
    """Persistence adapter for scan runs and their per-symbol results."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def save_scan(
        self,
        strategy_name: str,
        asset_type: str,
        results: list[ScanResult],
    ) -> int:
        """Persist a completed scan run and its results.

        Returns the new scan_run id.
        """

        now = datetime.now(UTC)

        with self._session_factory() as session:
            run = ScanRun(
                strategy_name=strategy_name,
                asset_type=asset_type,
                universe_size=len(results),
                started_at=now,
                completed_at=now,
            )
            session.add(run)
            session.flush()  # assigns run.id without committing yet

            records = [
                ScanResultRecord(
                    scan_run_id=run.id,
                    symbol=result.symbol,
                    passed=result.passed,
                    condition_results=[
                        dataclasses.asdict(cr) for cr in result.condition_results
                    ],
                    scanned_at=result.scanned_at,
                )
                for result in results
            ]
            session.add_all(records)
            session.commit()

            return run.id

    def get_latest_run_results(
        self,
        strategy_name: str,
        asset_type: str = "equity",
    ) -> list[ScanResult]:
        """Return the most recent scan run's results for a strategy.

        Returns an empty list if the strategy has never been run.
        """

        with self._session_factory() as session:
            latest_run_id = session.execute(
                select(ScanRun.id)
                .where(
                    ScanRun.strategy_name == strategy_name,
                    ScanRun.asset_type == asset_type,
                )
                .order_by(ScanRun.started_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if latest_run_id is None:
                return []

            records = (
                session.execute(
                    select(ScanResultRecord).where(
                        ScanResultRecord.scan_run_id == latest_run_id
                    )
                )
                .scalars()
                .all()
            )

            return [_to_scan_result(record) for record in records]

    def get_passed_symbols(
        self,
        strategy_name: str,
        asset_type: str = "equity",
    ) -> list[str]:
        """Convenience read: just the symbols that passed the latest run."""

        return [
            result.symbol
            for result in self.get_latest_run_results(strategy_name, asset_type)
            if result.passed
        ]


def _to_scan_result(record: ScanResultRecord) -> ScanResult:
    return ScanResult(
        symbol=record.symbol,
        passed=record.passed,
        condition_results=[
            ConditionResult(**condition_result)
            for condition_result in record.condition_results
        ],
        scanned_at=record.scanned_at,
    )
