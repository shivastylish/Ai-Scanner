from __future__ import annotations

from ai_screener.core.exceptions import ValidationError
from ai_screener.indicators.base import Indicator


class IndicatorRegistry:
    """Registry for indicator calculators, keyed by indicator name.

    Which indicators run for a given scan/snapshot is config-driven (a
    list of names), not hardcoded, so new indicators can be added without
    changing calling code.
    """

    _indicators: dict[str, Indicator] = {}

    @classmethod
    def register(cls, indicator: Indicator) -> None:
        cls._indicators[indicator.name] = indicator

    @classmethod
    def get(cls, name: str) -> Indicator:
        if name not in cls._indicators:
            raise ValidationError(f"No indicator registered for '{name}'.")
        return cls._indicators[name]

    @classmethod
    def registered_indicators(cls) -> list[str]:
        return sorted(cls._indicators.keys())
