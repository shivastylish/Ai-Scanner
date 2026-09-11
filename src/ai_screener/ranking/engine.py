from __future__ import annotations

from dataclasses import dataclass

from ai_screener.ranking.factors import (
    CPRWidthFactor,
    MomentumFactor,
    ScoringFactor,
    TrendStrengthFactor,
    VolumeFactor,
)
from ai_screener.ranking.weights import DEFAULT_FACTOR_WEIGHTS
from ai_screener.scanner.results import ScanResult

DEFAULT_FACTORS: list[ScoringFactor] = [
    CPRWidthFactor(),
    TrendStrengthFactor(),
    VolumeFactor(),
    MomentumFactor(),
]


@dataclass(frozen=True)
class RankedResult:
    symbol: str

    #: Weighted composite of factor scores, 0-100 (higher = more
    #: favorable) - the star score shown in the product's own mockup.
    score: float

    #: NOTE (open product question, see roadmap doc): "confidence" is not
    #: quantitatively defined anywhere in the current docs. This is a
    #: stated default, not a settled definition - it measures evidence
    #: completeness (the fraction of scored factors that had real
    #: underlying data), 0-100, not how favorable that evidence is. A
    #: result can score low but still be reported with high confidence
    #: (clearly not a match), or score respectably but with low
    #: confidence (too little data to trust the score). Revisit this
    #: definition with the user before treating it as final.
    confidence: float

    factor_scores: dict[str, float]
    scan_result: ScanResult


class RankingEngine:
    """Ranks already-scanned, passing symbols by a weighted composite of
    pluggable ScoringFactors.

    Pure computation over Sprint 3's persisted ScanResults - no new data
    ingestion, no provider/repository calls of its own - so results are
    deterministic and reproducible given the same scan output.
    """

    def __init__(
        self,
        factors: list[ScoringFactor] | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        self._factors = factors if factors is not None else DEFAULT_FACTORS
        self._weights = weights if weights is not None else DEFAULT_FACTOR_WEIGHTS

    def rank(self, scan_results: list[ScanResult]) -> list[RankedResult]:
        """Rank the symbols that passed their scan, best first.

        Symbols that did not pass the scan are excluded - ranking chooses
        among opportunities the scanner already identified, it does not
        override the scanner's own pass/fail decision.
        """

        ranked = [
            self._rank_one(scan_result)
            for scan_result in scan_results
            if scan_result.passed
        ]

        ranked.sort(key=lambda result: result.score, reverse=True)
        return ranked

    def _rank_one(self, scan_result: ScanResult) -> RankedResult:
        factor_scores = {
            factor.name: factor.score(scan_result) for factor in self._factors
        }

        total_weight = sum(
            self._weights.get(factor.name, 0.0) for factor in self._factors
        )
        weighted_sum = sum(
            factor_scores[factor.name] * self._weights.get(factor.name, 0.0)
            for factor in self._factors
        )
        composite = weighted_sum / total_weight if total_weight else 0.0

        return RankedResult(
            symbol=scan_result.symbol,
            score=round(composite * 100, 2),
            confidence=scan_result.evidence_completeness(),
            factor_scores={k: round(v, 4) for k, v in factor_scores.items()},
            scan_result=scan_result,
        )
