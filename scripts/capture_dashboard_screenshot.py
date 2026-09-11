"""Launch the real dashboard against the real dev database (already
seeded by verify_full_pipeline.py) and save a screenshot, so the
rendered UI can be inspected without an interactive display - e.g. under
QT_QPA_PLATFORM=offscreen, where no window is actually shown on screen.

Uses a deliberately lenient narrow-CPR threshold instead of the strict
monthly-narrow-CPR default, purely so the table has rows to look at for
this screenshot - the real app should be run with
scanner.strategies.monthly_narrow_cpr_strategy() for actual use.

Run with:

    uv run python scripts/capture_dashboard_screenshot.py
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from ai_screener.config.watchlist import get_watchlist
from ai_screener.dashboard.bootstrap import build_dashboard_controller
from ai_screener.dashboard.main_window import MainWindow
from ai_screener.scanner.rules import build_strategy

# A generous threshold (real values today range ~1-4.6%, per
# demo_inspect_indicators.py) purely so the table has rows to look at -
# the real app should be run with
# scanner.strategies.monthly_narrow_cpr_strategy()'s much stricter 0.5%.
_DEMO_STRATEGY = {
    "name": "demo_wide_cpr",
    "conditions": [
        {
            "type": "narrow_cpr",
            "params": {"max_width_pct": 10.0, "timeframe": "monthly"},
        },
    ],
}


def main() -> None:
    app = QApplication.instance() or QApplication([])

    controller = build_dashboard_controller()
    strategy = build_strategy(_DEMO_STRATEGY)
    window = MainWindow(
        controller=controller, universe=get_watchlist(), strategy=strategy
    )
    window.resize(1100, 700)
    window.show()

    window.run_scan()

    # Force a layout pass before grabbing, since offscreen windows don't
    # get an automatic paint event the way a real displayed window would.
    app.processEvents()

    pixmap = window.grab()
    pixmap.save("scripts/dashboard_screenshot.png")
    print("Saved scripts/dashboard_screenshot.png")
    print(f"Rows in table: {window._model.rowCount()}")
    print(f"Status: {window._status_label.text()}")


if __name__ == "__main__":
    main()
