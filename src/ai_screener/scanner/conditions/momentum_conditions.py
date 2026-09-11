from __future__ import annotations

from ai_screener.scanner.conditions.base import Condition, ConditionResult, to_float
from ai_screener.scanner.context import ScanContext


class MomentumPositiveCondition(Condition):
    """Momentum confirmation: is RSI above the neutral threshold?"""

    name = "momentum_positive"

    def __init__(self, rsi_period: int = 14, rsi_threshold: float = 50.0) -> None:
        self._rsi_period = rsi_period
        self._rsi_threshold = rsi_threshold
        self._key = f"rsi_rsi_{rsi_period}"

    def evaluate(self, context: ScanContext) -> ConditionResult:
        rsi_value = to_float(context.indicators.get(self._key))

        if rsi_value is None:
            return ConditionResult(
                condition_name=self.name,
                passed=False,
                value=None,
                threshold=self._rsi_threshold,
                description=f"No RSI({self._rsi_period}) data available yet.",
            )

        passed = rsi_value > self._rsi_threshold

        return ConditionResult(
            condition_name=self.name,
            passed=passed,
            value=round(rsi_value, 2),
            threshold=self._rsi_threshold,
            description=(
                f"RSI({self._rsi_period}) is {rsi_value:.2f} "
                f"({'>' if passed else '<='} {self._rsi_threshold} threshold)."
            ),
        )
