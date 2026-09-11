from __future__ import annotations

from ai_screener.scanner.conditions.base import Condition, ConditionResult, to_float
from ai_screener.scanner.context import ScanContext


class TrendAboveEMACondition(Condition):
    """Bullish-trend confirmation: is the close trading above its EMA?"""

    name = "trend_above_ema"

    def __init__(self, period: int = 20) -> None:
        self._period = period
        self._key = f"ema_ema_{period}"

    def evaluate(self, context: ScanContext) -> ConditionResult:
        ema_value = to_float(context.indicators.get(self._key))

        if context.history.empty or ema_value is None:
            return ConditionResult(
                condition_name=self.name,
                passed=False,
                value=None,
                threshold=None,
                description=f"No EMA({self._period}) data available yet.",
            )

        close = float(context.history["close"].iloc[-1])
        passed = close > ema_value

        return ConditionResult(
            condition_name=self.name,
            passed=passed,
            value=round(close, 4),
            threshold=round(ema_value, 4),
            description=(
                f"Close {close:.2f} is "
                f"{'above' if passed else 'not above'} "
                f"EMA({self._period}) {ema_value:.2f}."
            ),
        )
