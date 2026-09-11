from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fakes.fake_provider import FakeEquityProvider
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backtesting's ORM models are registered on Base.metadata too.
from ai_screener.backtesting import db_models as _backtesting_models  # noqa: F401
from ai_screener.backtesting.engine import BacktestEngine
from ai_screener.backtesting.repositories.backtest_repository import (
    BacktestRepository,
)
from ai_screener.dashboard.controller import DashboardController
from ai_screener.database.session import initialize_database

# Ensure explainability's ORM models are registered on Base.metadata too.
from ai_screener.explainability import db_models as _explainability_models  # noqa: F401
from ai_screener.explainability.repositories.explanation_repository import (
    ExplanationRepository,
)
from ai_screener.explainability.service import ExplainabilityService
from ai_screener.indicators.bootstrap import register_default_indicators
from ai_screener.indicators.service import IndicatorService
from ai_screener.journal.repositories.journal_repository import JournalRepository
from ai_screener.journal.service import JournalService
from ai_screener.market_data.mutual_funds.repositories.fund_nav_repository import (
    FundNavRepository,
)
from ai_screener.market_data.normalization import NormalizerRegistry, YahooNormalizer
from ai_screener.market_data.providers import ProviderRegistry
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)
from ai_screener.market_data.services import MarketDataService
from ai_screener.portfolio.repositories.portfolio_repository import (
    PortfolioRepository,
)
from ai_screener.portfolio.service import PortfolioService
from ai_screener.ranking.engine import RankingEngine

# Ensure every domain's ORM models are registered on Base.metadata before
# any fixture below calls initialize_database() - mirrors alembic/env.py.
from ai_screener.scanner import models as _scanner_models  # noqa: F401
from ai_screener.scanner.engine import ScannerEngine
from ai_screener.scanner.repositories.scan_result_repository import (
    ScanResultRepository,
)

# Run Qt headlessly (no real display needed/available in CI or this
# environment). Must be set before any PySide6 import; this runs once,
# here, before pytest imports any test module (dashboard tests import
# PySide6 at module level), and after every plain import above so ruff's
# import-order check stays happy.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Every fixture below is hermetic: an in-memory SQLite database (shared
# across connections via StaticPool, since a bare "sqlite://" gives every
# new connection its own throwaway database) and a fake provider that never
# touches the network. This is the pattern every later sprint's tests
# should reuse instead of hitting the real dev database or a live API.


@pytest.fixture
def db_engine() -> Iterator[Engine]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    initialize_database(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def session_factory(db_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker[Session](
        bind=db_engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


@pytest.fixture
def repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> MarketDataRepository:
    return MarketDataRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )


@pytest.fixture
def fake_equity_provider() -> FakeEquityProvider:
    return FakeEquityProvider()


@pytest.fixture
def registered_fake_provider(
    fake_equity_provider: FakeEquityProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> FakeEquityProvider:
    """Register the fake provider for "equity" plus the real Yahoo normalizer.

    Reuses the real YahooNormalizer/Pipeline so tests exercise the actual
    normalization/validation logic; only the network-touching provider is
    swapped out. Registrations are scoped to the test via monkeypatch.
    """

    monkeypatch.setitem(NormalizerRegistry._normalizers, "yahoo", YahooNormalizer())
    monkeypatch.setitem(ProviderRegistry._providers, "equity", fake_equity_provider)
    return fake_equity_provider


@pytest.fixture
def service(
    repository: MarketDataRepository,
    registered_fake_provider: FakeEquityProvider,
) -> MarketDataService:
    return MarketDataService(repository=repository)


@pytest.fixture
def indicator_service(service: MarketDataService) -> IndicatorService:
    register_default_indicators()
    return IndicatorService(market_data_service=service)


@pytest.fixture
def scan_repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> ScanResultRepository:
    return ScanResultRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )


@pytest.fixture
def scanner_engine(
    service: MarketDataService,
    indicator_service: IndicatorService,
    scan_repository: ScanResultRepository,
) -> ScannerEngine:
    return ScannerEngine(
        market_data_service=service,
        indicator_service=indicator_service,
        repository=scan_repository,
    )


@pytest.fixture
def explanation_repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> ExplanationRepository:
    return ExplanationRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )


@pytest.fixture
def explainability_service(
    explanation_repository: ExplanationRepository,
) -> ExplainabilityService:
    return ExplainabilityService(repository=explanation_repository)


@pytest.fixture
def backtest_repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> BacktestRepository:
    return BacktestRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )


@pytest.fixture
def backtest_engine(
    service: MarketDataService,
    indicator_service: IndicatorService,
    backtest_repository: BacktestRepository,
) -> BacktestEngine:
    return BacktestEngine(
        market_data_service=service,
        indicator_service=indicator_service,
        repository=backtest_repository,
    )


@pytest.fixture
def ranking_engine() -> RankingEngine:
    return RankingEngine()


@pytest.fixture
def dashboard_controller(
    scanner_engine: ScannerEngine,
    ranking_engine: RankingEngine,
    explainability_service: ExplainabilityService,
    backtest_engine: BacktestEngine,
) -> DashboardController:
    return DashboardController(
        scanner_engine=scanner_engine,
        ranking_engine=ranking_engine,
        explainability_service=explainability_service,
        backtest_engine=backtest_engine,
    )


@pytest.fixture
def portfolio_repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> PortfolioRepository:
    return PortfolioRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )


@pytest.fixture
def portfolio_service(
    portfolio_repository: PortfolioRepository,
    service: MarketDataService,
) -> PortfolioService:
    return PortfolioService(
        repository=portfolio_repository, market_data_service=service
    )


@pytest.fixture
def journal_repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> JournalRepository:
    return JournalRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )


@pytest.fixture
def journal_service(journal_repository: JournalRepository) -> JournalService:
    return JournalService(repository=journal_repository)


@pytest.fixture
def fund_nav_repository(
    db_engine: Engine, session_factory: sessionmaker[Session]
) -> FundNavRepository:
    return FundNavRepository(
        session_factory=session_factory,
        database_engine=db_engine,
    )
