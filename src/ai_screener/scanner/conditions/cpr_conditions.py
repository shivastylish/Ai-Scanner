from __future__ import annotations

from ai_screener.scanner.conditions.base import Condition, ConditionResult, to_float
from ai_screener.scanner.context import ScanContext


class NarrowCPRCondition(Condition):
    """The product's core screen: is this period's CPR unusually narrow?

    Reads ``cpr_{timeframe}_width_pct`` from the symbol's indicator
    snapshot (see IndicatorService / DEFAULT_INDICATORS).
    """

    name = "narrow_cpr"

    def __init__(self, max_width_pct: float = 0.5, timeframe: str = "monthly") -> None:
        self._max_width_pct = max_width_pct
        self._timeframe = timeframe
        self._key = f"cpr_{timeframe}_width_pct"

    def evaluate(self, context: ScanContext) -> ConditionResult:
        value = to_float(context.indicators.get(self._key))

        if value is None:
            return ConditionResult(
                condition_name=self.name,
                passed=False,
                value=None,
                threshold=self._max_width_pct,
                description=f"No {self._timeframe} CPR data available yet.",
            )

        passed = value <= self._max_width_pct

        return ConditionResult(
            condition_name=self.name,
            passed=passed,
            value=round(value, 4),
            threshold=self._max_width_pct,
            description=(
                f"{self._timeframe.title()} CPR width is {value:.2f}% "
                f"({'<=' if passed else '>'} {self._max_width_pct}% threshold)."
            ),
        )
