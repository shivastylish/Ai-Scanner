from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Reason:
    """One piece of evidence behind a recommendation - not a bare score.

    ``evidence`` carries the raw supporting numbers (e.g.
    ``{"width_pct": 0.32, "threshold": 0.5}``) so the dashboard can show
    its work, not just a sentence.
    """

    category: str
    statement: str
    value: Any
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Explanation:
    """The full "why selected" evidence set for one symbol.

    Per ADR-004 ("a score without evidence is not sufficient"), this is
    treated as a durable, audit-able artifact - generated at scan time
    and persisted (see ExplanationRepository), not recomputed on demand
    each time the dashboard renders it.
    """

    symbol: str
    reasons: list[Reason]
    confidence: float
    generated_at: datetime
