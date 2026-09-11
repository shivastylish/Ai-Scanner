from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ai_screener.core.exceptions import ValidationError
from ai_screener.scanner.conditions.base import Condition, ConditionResult
from ai_screener.scanner.conditions.cpr_conditions import NarrowCPRCondition
from ai_screener.scanner.conditions.momentum_conditions import MomentumPositiveCondition
from ai_screener.scanner.conditions.trend_conditions import TrendAboveEMACondition
from ai_screener.scanner.conditions.volume_conditions import VolumeAboveAverageCondition
from ai_screener.scanner.context import ScanContext

#: Maps a condition "type" name (as used in a strategy spec) to its class.
# A strategy spec is plain data (dict), so new strategies - or, later, a
# YAML/JSON strategy file loader - can be added without touching the
# scanner engine, per ADR-008 (configuration over hardcoding).
CONDITION_FACTORY: dict[str, type[Condition]] = {
    "narrow_cpr": NarrowCPRCondition,
    "trend_above_ema": TrendAboveEMACondition,
    "volume_above_average": VolumeAboveAverageCondition,
    "momentum_positive": MomentumPositiveCondition,
}


@dataclass(frozen=True)
class StrategyResult:
    passed: bool
    condition_results: list[ConditionResult]


class ScanRule(ABC):
    """Composes one or more Conditions into a pass/fail decision."""

    @abstractmethod
    def evaluate(self, context: ScanContext) -> StrategyResult:
        """Evaluate every condition and combine their results."""


class AllOf(ScanRule):
    """Passes only if every condition passes."""

    def __init__(self, conditions: list[Condition]) -> None:
        self._conditions = conditions

    def evaluate(self, context: ScanContext) -> StrategyResult:
        results = [condition.evaluate(context) for condition in self._conditions]
        return StrategyResult(
            passed=all(result.passed for result in results),
            condition_results=results,
        )


class AnyOf(ScanRule):
    """Passes if at least one condition passes."""

    def __init__(self, conditions: list[Condition]) -> None:
        self._conditions = conditions

    def evaluate(self, context: ScanContext) -> StrategyResult:
        results = [condition.evaluate(context) for condition in self._conditions]
        return StrategyResult(
            passed=any(result.passed for result in results),
            condition_results=results,
        )


@dataclass(frozen=True)
class ScanStrategy:
    name: str
    rule: ScanRule


def build_condition(spec: dict[str, Any]) -> Condition:
    """Build a Condition from a ``{"type": ..., "params": {...}}`` spec."""

    condition_type = spec["type"]

    if condition_type not in CONDITION_FACTORY:
        raise ValidationError(f"Unknown condition type: '{condition_type}'.")

    condition_class = CONDITION_FACTORY[condition_type]
    return condition_class(**spec.get("params", {}))


def build_strategy(spec: dict[str, Any]) -> ScanStrategy:
    """Build a ScanStrategy from a plain-data spec.

    ``spec`` shape::

        {
            "name": "monthly_narrow_cpr",
            "rule": "all_of",  # or "any_of"
            "conditions": [
                {"type": "narrow_cpr", "params": {"max_width_pct": 0.5}},
                ...
            ],
        }
    """

    conditions = [build_condition(c) for c in spec["conditions"]]
    rule_type = spec.get("rule", "all_of")

    if rule_type == "all_of":
        rule: ScanRule = AllOf(conditions)
    elif rule_type == "any_of":
        rule = AnyOf(conditions)
    else:
        raise ValidationError(f"Unknown rule type: '{rule_type}'.")

    return ScanStrategy(name=spec["name"], rule=rule)
