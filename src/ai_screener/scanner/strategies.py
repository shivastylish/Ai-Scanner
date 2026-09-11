from __future__ import annotations

from typing import Any

from ai_screener.scanner.rules import ScanStrategy, build_strategy

#: The product's original core idea (see the project summary): flag
#: stocks with an unusually narrow Monthly CPR, confirmed by trend,
#: volume, and momentum. A strategy spec is plain data - swap or extend
#: this dict (or load one from a config file later) without touching the
#: scanner engine.
MONTHLY_NARROW_CPR_STRATEGY_SPEC: dict[str, Any] = {
    "name": "monthly_narrow_cpr",
    "rule": "all_of",
    "conditions": [
        {
            "type": "narrow_cpr",
            "params": {"max_width_pct": 0.5, "timeframe": "monthly"},
        },
        {
            "type": "trend_above_ema",
            "params": {"period": 20},
        },
        {
            "type": "volume_above_average",
            "params": {"lookback": 20, "multiplier": 1.0},
        },
        {
            "type": "momentum_positive",
            "params": {"rsi_period": 14, "rsi_threshold": 50.0},
        },
    ],
}


def monthly_narrow_cpr_strategy() -> ScanStrategy:
    return build_strategy(MONTHLY_NARROW_CPR_STRATEGY_SPEC)
