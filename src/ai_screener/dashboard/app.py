"""Dashboard entry point.

Run with:

    uv run python -m ai_screener.dashboard.app
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ai_screener.config.watchlist import get_watchlist
from ai_screener.dashboard.bootstrap import build_dashboard_controller
from ai_screener.dashboard.main_window import MainWindow
from ai_screener.scanner.strategies import monthly_narrow_cpr_strategy


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)

    controller = build_dashboard_controller()
    window = MainWindow(
        controller=controller,
        universe=get_watchlist(),
        strategy=monthly_narrow_cpr_strategy(),
    )
    window.resize(1000, 650)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
