"""Manual smoke check: print real computed indicator values for the
watchlist, so a 0-pass scan can be told apart from a broken one.

Run with:

    uv run python scripts/verify_indicators.py
"""

from __future__ import annotations

from ai_screener.config.watchlist import get_watchlist
from ai_screener.indicators.bootstrap import register_default_indicators
from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.providers.bootstrap import register_default_providers
from ai_screener.market_data.services import MarketDataService


def main() -> None:
    register_default_providers()
    register_default_indicators()

    market_data_service = MarketDataService()
    indicator_service = IndicatorService(market_data_service=market_data_service)

    print(
        f"{'Symbol':<15} {'Close':>10} {'EMA20':>10} {'RSI14':>7} "
        f"{'MonthlyCPR%':>12} {'WeeklyCPR%':>11} {'DailyCPR%':>10}"
    )
    for symbol in get_watchlist():
        latest = indicator_service.latest(symbol)
        history = market_data_service.get_history(symbol)
        close = history["close"].iloc[-1] if not history.empty else float("nan")

        print(
            f"{symbol:<15} {close:>10.2f} "
            f"{latest.get('ema_ema_20', float('nan')):>10.2f} "
            f"{latest.get('rsi_rsi_14', float('nan')):>7.1f} "
            f"{latest.get('cpr_monthly_width_pct', float('nan')):>12.2f} "
            f"{latest.get('cpr_weekly_width_pct', float('nan')):>11.2f} "
            f"{latest.get('cpr_daily_width_pct', float('nan')):>10.2f}"
        )


if __name__ == "__main__":
    main()
