from __future__ import annotations

#: Weighted-sum config (ADR-008: configurable, not hardcoded). Keys must
#: match a registered ScoringFactor's ``name``. Weights need not sum to 1
#: - RankingEngine normalizes by the total weight actually applied.
DEFAULT_FACTOR_WEIGHTS: dict[str, float] = {
    "cpr_width": 0.4,
    "trend_strength": 0.2,
    "volume": 0.2,
    "momentum": 0.2,
}
