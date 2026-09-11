from __future__ import annotations

from PySide6.QtCore import Qt

from ai_screener.dashboard.controller import DashboardController
from ai_screener.dashboard.main_window import MainWindow
from ai_screener.market_data.services import MarketDataService
from ai_screener.scanner.rules import build_strategy

_ALWAYS_RELEVANT_STRATEGY = {
    "name": "always_relevant",
    "conditions": [
        {
            "type": "narrow_cpr",
            "params": {"max_width_pct": 999.0, "timeframe": "daily"},
        }
    ],
}


def test_run_scan_populates_the_table(
    qtbot,
    service: MarketDataService,
    dashboard_controller: DashboardController,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    strategy = build_strategy(_ALWAYS_RELEVANT_STRATEGY)
    window = MainWindow(
        controller=dashboard_controller,
        universe=["RELIANCE.NS"],
        strategy=strategy,
    )
    qtbot.addWidget(window)

    window.run_scan()

    assert window._model.rowCount() == 1
    assert "1 symbol(s) passed" in window._status_label.text()


def test_selecting_a_row_shows_its_explanation(
    qtbot,
    service: MarketDataService,
    dashboard_controller: DashboardController,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    strategy = build_strategy(_ALWAYS_RELEVANT_STRATEGY)
    window = MainWindow(
        controller=dashboard_controller,
        universe=["RELIANCE.NS"],
        strategy=strategy,
    )
    qtbot.addWidget(window)
    window.run_scan()

    index = window._model.index(0, 0)
    window._table.selectionModel().setCurrentIndex(
        index, window._table.selectionModel().SelectionFlag.ClearAndSelect
    )

    assert "RELIANCE.NS" in window._explanation_panel._title.text()


def test_run_scan_with_no_passing_symbols_shows_message(
    qtbot,
    dashboard_controller: DashboardController,
) -> None:
    strategy = build_strategy(_ALWAYS_RELEVANT_STRATEGY)
    window = MainWindow(
        controller=dashboard_controller,
        universe=["UNKNOWN.NS"],
        strategy=strategy,
    )
    qtbot.addWidget(window)

    window.run_scan()

    assert window._model.rowCount() == 0
    assert "No symbols passed" in window._status_label.text()


def test_run_scan_button_triggers_scan(
    qtbot,
    service: MarketDataService,
    dashboard_controller: DashboardController,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    strategy = build_strategy(_ALWAYS_RELEVANT_STRATEGY)
    window = MainWindow(
        controller=dashboard_controller,
        universe=["RELIANCE.NS"],
        strategy=strategy,
    )
    qtbot.addWidget(window)

    qtbot.mouseClick(window._scan_button, Qt.MouseButton.LeftButton)

    assert window._model.rowCount() == 1
