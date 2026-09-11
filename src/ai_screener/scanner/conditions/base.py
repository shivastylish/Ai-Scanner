from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ai_screener.scanner.context import ScanContext


def is_missing(value: Any) -> bool:
    """True for None or NaN - the two "no data yet" shapes indicator
    values can take (a missing dict key resolves to None via .get())."""

    return value is None or (isinstance(value, float) and math.isnan(value))


def to_float(value: Any) -> float | None:
    """Coerce an indicator value to float, or None if it's missing.

    Prefer this over a separate is_missing() check in conditions: a plain
    ``if value is None: ...`` after this narrows cleanly under mypy,
    whereas branching on the opaque is_missing() call does not.
    """

    if is_missing(value):
        return None
    return float(value)


@dataclass(frozen=True)
class ConditionResult:
    """A structured, explainable outcome - not a bare bool.

    Kept structured from day one (Sprint 3) so the explainability engine
    (Sprint 5) and dashboard can render *why* a condition passed or
    failed without needing richer output retrofitted later.
    """

    condition_name: str
    passed: bool
    value: Any
    threshold: Any
    description: str


class Condition(ABC):
    """Base interface for a single scan condition."""

    #: Registry/display name. Subclasses must override.
    name: str

    @abstractmethod
    def evaluate(self, context: ScanContext) -> ConditionResult:
        """Evaluate this condition for one symbol."""
