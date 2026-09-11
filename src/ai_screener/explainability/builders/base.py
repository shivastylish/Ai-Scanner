from __future__ import annotations

from abc import ABC, abstractmethod

from ai_screener.explainability.models import Reason
from ai_screener.ranking.engine import RankedResult
from ai_screener.scanner.results import ScanResult


class ReasonBuilder(ABC):
    """Turns evidence already captured by the scanner/ranker into one
    human-readable Reason, or None if it has nothing to say for this
    symbol (e.g. the underlying condition had no data).

    Reads only from ScanResult.condition_results and RankedResult -
    never re-fetches indicators or market data - so explanations are a
    pure function of already-persisted scan output, same discipline as
    the ranking engine.
    """

    #: Reason.category this builder produces. Subclasses must override.
    category: str

    @abstractmethod
    def build(
        self, scan_result: ScanResult, ranked_result: RankedResult | None
    ) -> Reason | None:
        """Build this builder's Reason for one symbol, or None."""
