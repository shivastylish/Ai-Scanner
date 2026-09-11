from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.dashboard.widgets.explanation_panel import ExplanationPanel
from ai_screener.explainability.models import Explanation, Reason


def test_shows_placeholder_before_any_selection(qtbot) -> None:
    panel = ExplanationPanel()
    qtbot.addWidget(panel)

    assert "Select a symbol" in panel._title.text()
    assert panel._reason_list.count() == 0


def test_show_explanation_renders_title_and_reasons(qtbot) -> None:
    panel = ExplanationPanel()
    qtbot.addWidget(panel)

    explanation = Explanation(
        symbol="RELIANCE.NS",
        reasons=[
            Reason(
                category="cpr",
                statement="Monthly CPR width is 0.30%.",
                value=0.3,
                evidence={"width_pct": 0.3},
            ),
            Reason(
                category="momentum",
                statement="RSI is 65.",
                value=65.0,
                evidence={"rsi": 65.0},
            ),
        ],
        confidence=87.5,
        generated_at=datetime.now(UTC),
    )

    panel.show_explanation("RELIANCE.NS", explanation)

    assert "RELIANCE.NS" in panel._title.text()
    assert "88%" in panel._title.text() or "87" in panel._title.text()
    assert panel._reason_list.count() == 2
    assert "cpr" in panel._reason_list.item(0).text()
    assert "momentum" in panel._reason_list.item(1).text()


def test_show_explanation_with_no_reasons_shows_fallback_message(qtbot) -> None:
    panel = ExplanationPanel()
    qtbot.addWidget(panel)

    explanation = Explanation(
        symbol="TCS.NS", reasons=[], confidence=0.0, generated_at=datetime.now(UTC)
    )

    panel.show_explanation("TCS.NS", explanation)

    assert panel._reason_list.count() == 1
    assert "No supporting evidence" in panel._reason_list.item(0).text()


def test_clear_resets_to_placeholder(qtbot) -> None:
    panel = ExplanationPanel()
    qtbot.addWidget(panel)

    explanation = Explanation(
        symbol="TCS.NS",
        reasons=[Reason("cpr", "x", 1, {})],
        confidence=50.0,
        generated_at=datetime.now(UTC),
    )
    panel.show_explanation("TCS.NS", explanation)

    panel.clear()

    assert "Select a symbol" in panel._title.text()
    assert panel._reason_list.count() == 0
