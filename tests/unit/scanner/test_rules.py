from __future__ import annotations

import pytest

from ai_screener.core.exceptions import ValidationError
from ai_screener.scanner.conditions.base import Condition, ConditionResult
from ai_screener.scanner.context import ScanContext
from ai_screener.scanner.rules import AllOf, AnyOf, build_condition, build_strategy


class StubCondition(Condition):
    """A condition with a fixed outcome, for testing rule composition."""

    name = "stub"

    def __init__(self, passed: bool) -> None:
        self._passed = passed

    def evaluate(self, context: ScanContext) -> ConditionResult:
        return ConditionResult(
            condition_name=self.name,
            passed=self._passed,
            value=None,
            threshold=None,
            description="stub",
        )


def _context() -> ScanContext:
    import pandas as pd

    return ScanContext(symbol="TEST.NS", history=pd.DataFrame(), indicators={})


class TestAllOf:
    def test_passes_when_every_condition_passes(self) -> None:
        rule = AllOf([StubCondition(True), StubCondition(True)])
        result = rule.evaluate(_context())

        assert result.passed is True
        assert len(result.condition_results) == 2

    def test_fails_when_any_condition_fails(self) -> None:
        rule = AllOf([StubCondition(True), StubCondition(False)])
        result = rule.evaluate(_context())

        assert result.passed is False


class TestAnyOf:
    def test_passes_when_at_least_one_condition_passes(self) -> None:
        rule = AnyOf([StubCondition(False), StubCondition(True)])
        result = rule.evaluate(_context())

        assert result.passed is True

    def test_fails_when_every_condition_fails(self) -> None:
        rule = AnyOf([StubCondition(False), StubCondition(False)])
        result = rule.evaluate(_context())

        assert result.passed is False


class TestBuildStrategy:
    def test_builds_all_of_strategy_from_spec(self) -> None:
        spec = {
            "name": "test_strategy",
            "rule": "all_of",
            "conditions": [
                {"type": "narrow_cpr", "params": {"max_width_pct": 1.0}},
                {"type": "momentum_positive", "params": {"rsi_threshold": 50.0}},
            ],
        }

        strategy = build_strategy(spec)

        assert strategy.name == "test_strategy"
        assert isinstance(strategy.rule, AllOf)

    def test_builds_any_of_strategy_from_spec(self) -> None:
        spec = {
            "name": "test_strategy",
            "rule": "any_of",
            "conditions": [{"type": "momentum_positive", "params": {}}],
        }

        strategy = build_strategy(spec)

        assert isinstance(strategy.rule, AnyOf)

    def test_unknown_condition_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            build_condition({"type": "not_a_real_condition"})

    def test_unknown_rule_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            build_strategy(
                {
                    "name": "bad",
                    "rule": "not_a_real_rule",
                    "conditions": [{"type": "momentum_positive", "params": {}}],
                }
            )
