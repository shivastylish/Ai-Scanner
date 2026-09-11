from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class Indicator(ABC):
    """Base interface for all indicator calculators.

    An Indicator consumes an OHLCV DataFrame (columns at least
    "datetime", "open", "high", "low", "close", "volume", ordered
    ascending by datetime) and returns a new DataFrame containing a
    "datetime" column plus the indicator's own output columns. It must
    never mutate the input frame.

    Each concrete calculator narrows ``**params: Any`` to its own named,
    defaulted keyword arguments (e.g. ``period: int = 14``) for a
    self-documenting call signature; that narrowing is a deliberate
    plugin-style API choice, so subclasses carry a
    ``# type: ignore[override]`` for mypy's (correct, but here
    intentional) Liskov substitution check.
    """

    #: Registry key. Subclasses must override.
    name: str

    @abstractmethod
    def compute(self, df: pd.DataFrame, **params: Any) -> pd.DataFrame:
        """Compute the indicator over the given OHLCV history."""
