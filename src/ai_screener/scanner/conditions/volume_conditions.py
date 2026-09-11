from __future__ import annotations

from ai_screener.scanner.conditions.base import Condition, ConditionResult
from ai_screener.scanner.context import ScanContext


class VolumeAboveAverageCondition(Condition):
    """Volume confirmation: is today's volume above its recent average?

    Computed directly from history rather than the indicator snapshot,
    since it is a simple rolling statistic rather than a registered
    Indicator.
    """

    name = "volume_above_average"

    def __init__(self, lookback: int = 20, multiplier: float = 1.0) -> None:
        self._lookback = lookback
        self._multiplier = multiplier

    def evaluate(self, context: ScanContext) -> ConditionResult:
        volume = context.history["volume"]

        # Compare today's volume against the average of the preceding
        # `lookback` days, excluding today itself.
        if len(volume) < self._lookback + 1:
            return ConditionResult(
                condition_name=self.name,
                passed=False,
                value=None,
                threshold=None,
                description=(
                    f"Not enough history for a {self._lookback}-day "
                    "volume average yet."
                ),
            )

        today_volume = float(volume.iloc[-1])
        average_volume = float(volume.iloc[-(self._lookback + 1) : -1].mean())
        threshold = average_volume * self._multiplier
        passed = today_volume > threshold

        return ConditionResult(
            condition_name=self.name,
            passed=passed,
            value=round(today_volume, 2),
            threshold=round(threshold, 2),
            description=(
                f"Volume {today_volume:,.0f} is "
                f"{'above' if passed else 'not above'} "
                f"{self._multiplier:g}x the {self._lookback}-day average "
                f"({average_volume:,.0f})."
            ),
        )
