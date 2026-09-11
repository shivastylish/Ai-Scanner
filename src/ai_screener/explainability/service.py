from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.explainability.builders import DEFAULT_BUILDERS, ReasonBuilder
from ai_screener.explainability.models import Explanation
from ai_screener.explainability.repositories.explanation_repository import (
    ExplanationRepository,
)
from ai_screener.ranking.engine import RankedResult
from ai_screener.scanner.results import ScanResult


class ExplainabilityService:
    """Builds and (by default) persists the "why selected" evidence for
    one symbol's scan result.

    Runs at scan-time, not at dashboard-render-time - explanations are
    durable artifacts (ADR-004), not recomputed on every view.
    """

    def __init__(
        self,
        builders: list[ReasonBuilder] | None = None,
        repository: ExplanationRepository | None = None,
    ) -> None:
        self._builders = builders if builders is not None else DEFAULT_BUILDERS
        self._repository = repository

    def explain(
        self,
        scan_result: ScanResult,
        ranked_result: RankedResult | None = None,
        persist: bool = True,
    ) -> Explanation:
        reasons = [
            reason
            for reason in (
                builder.build(scan_result, ranked_result) for builder in self._builders
            )
            if reason is not None
        ]

        confidence = (
            ranked_result.confidence
            if ranked_result is not None
            else scan_result.evidence_completeness()
        )

        explanation = Explanation(
            symbol=scan_result.symbol,
            reasons=reasons,
            confidence=confidence,
            generated_at=datetime.now(UTC),
        )

        if persist and self._repository is not None:
            self._repository.save(explanation)

        return explanation
