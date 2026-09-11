"""Manual smoke check: real live data through the entire pipeline.

Downloads real history for the default watchlist (equities), a crypto
pair, and a mutual fund scheme, then runs the full
Scanner -> Ranking -> Explainability chain over the equities and prints
a summary. This intentionally writes into the real dev database
(data/ai_screener.db) - that's the whole point of a manual run, unlike
the test suite which must stay hermetic.

Run with:

    uv run python scripts/verify_full_pipeline.py
"""

from __future__ import annotations

from ai_screener.config.watchlist import get_watchlist
from ai_screener.explainability.repositories.explanation_repository import (
    ExplanationRepository,
)
from ai_screener.explainability.service import ExplainabilityService
from ai_screener.indicators.bootstrap import register_default_indicators
from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.mutual_funds.service import MutualFundService
from ai_screener.market_data.providers.bootstrap import register_default_providers
from ai_screener.market_data.services import MarketDataService
from ai_screener.ranking.engine import RankingEngine
from ai_screener.scanner.engine import ScannerEngine
from ai_screener.scanner.repositories.scan_result_repository import (
    ScanResultRepository,
)
from ai_screener.scanner.strategies import monthly_narrow_cpr_strategy

START_DATE = "2024-01-01"


def main() -> None:
    register_default_providers()
    register_default_indicators()

    market_data_service = MarketDataService()
    indicator_service = IndicatorService(market_data_service=market_data_service)
    scanner_engine = ScannerEngine(
        market_data_service=market_data_service,
        indicator_service=indicator_service,
        repository=ScanResultRepository(),
    )
    ranking_engine = RankingEngine()
    explainability_service = ExplainabilityService(repository=ExplanationRepository())

    watchlist = get_watchlist()
    print(f"=== Downloading equity history for {len(watchlist)} symbols ===")
    for symbol in watchlist:
        try:
            df = market_data_service.download_history(
                symbol=symbol, start_date=START_DATE
            )
            print(f"  {symbol}: {len(df)} rows")
        except Exception as exc:  # noqa: BLE001 - demo script, report and continue
            print(f"  {symbol}: FAILED ({exc})")

    print("\n=== Downloading crypto history (Binance + CoinGecko) ===")
    for provider_name, symbol in [("binance", "BTCUSDT"), ("coingecko", "bitcoin")]:
        try:
            df = market_data_service.download_history(
                symbol=symbol,
                asset_type="crypto",
                start_date="2025-08-01",
                provider_name=provider_name,
            )
            print(f"  {provider_name}/{symbol}: {len(df)} rows")
        except Exception as exc:  # noqa: BLE001
            print(f"  {provider_name}/{symbol}: FAILED ({exc})")

    print("\n=== Downloading a mutual fund NAV history ===")
    mutual_fund_service = MutualFundService()
    try:
        df = mutual_fund_service.download_history(
            scheme_code="119551", start_date="2025-01-01"
        )
        print(f"  scheme 119551: {len(df)} NAV rows")
    except Exception as exc:  # noqa: BLE001
        print(f"  scheme 119551: FAILED ({exc})")

    print("\n=== Running the Monthly Narrow CPR scan ===")
    strategy = monthly_narrow_cpr_strategy()
    scan_results = scanner_engine.scan(universe=watchlist, strategy=strategy)
    passed = [r for r in scan_results if r.passed]
    print(f"  {len(passed)}/{len(scan_results)} symbols passed.")

    print("\n=== Ranking ===")
    ranked = ranking_engine.rank(scan_results)
    for r in ranked:
        print(f"  {r.symbol:<15} score={r.score:6.2f}  confidence={r.confidence:5.1f}%")

    print("\n=== Explainability (top result) ===")
    if ranked:
        top = ranked[0]
        explanation = explainability_service.explain(top.scan_result, top)
        print(f"  {top.symbol} (confidence {explanation.confidence:.0f}%):")
        for reason in explanation.reasons:
            print(f"    [{reason.category}] {reason.statement}")
    else:
        print("  No symbols passed the scan with real current market data.")

    print(
        f"\n=== Total rows now in market_data table: "
        f"{market_data_service.get_row_count()} ==="
    )


if __name__ == "__main__":
    main()
