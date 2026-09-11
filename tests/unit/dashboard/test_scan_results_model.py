from __future__ import annotations

from datetime import UTC, datetime

from PySide6.QtCore import QModelIndex, Qt

from ai_screener.dashboard.controller import DashboardRow
from ai_screener.dashboard.viewmodels.scan_results_model import ScanResultsTableModel
from ai_screener.explainability.models import Explanation
from ai_screener.ranking.engine import RankedResult
from ai_screener.scanner.results import ScanResult


def _row(
    symbol: str, score: float, confidence: float, backtested: bool
) -> DashboardRow:
    scan_result = ScanResult(
        symbol=symbol, passed=True, condition_results=[], scanned_at=datetime.now(UTC)
    )
    ranked_result = RankedResult(
        symbol=symbol,
        score=score,
        confidence=confidence,
        factor_scores={},
        scan_result=scan_result,
    )
    explanation = Explanation(
        symbol=symbol, reasons=[], confidence=confidence, generated_at=datetime.now(UTC)
    )
    return DashboardRow(
        ranked_result=ranked_result, explanation=explanation, is_backtested=backtested
    )


def test_empty_model_has_zero_rows(qtbot) -> None:
    model = ScanResultsTableModel()

    assert model.rowCount() == 0
    assert model.columnCount() == 4


def test_set_rows_populates_the_model(qtbot) -> None:
    model = ScanResultsTableModel()

    model.set_rows(
        [
            _row("RELIANCE.NS", 82.5, 100.0, True),
            _row("TCS.NS", 60.0, 50.0, False),
        ]
    )

    assert model.rowCount() == 2

    first = model.index(0, 0)
    assert model.data(first, Qt.ItemDataRole.DisplayRole) == "RELIANCE.NS"

    score_cell = model.index(0, 1)
    assert model.data(score_cell) == "82.5"

    confidence_cell = model.index(0, 2)
    assert model.data(confidence_cell) == "100%"

    backtested_cell = model.index(0, 3)
    assert model.data(backtested_cell) == "Yes"

    second_backtested_cell = model.index(1, 3)
    assert model.data(second_backtested_cell) == "No"


def test_header_data_returns_column_names(qtbot) -> None:
    model = ScanResultsTableModel()

    assert (
        model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        == "Symbol"
    )


def test_row_at_returns_the_underlying_dashboard_row(qtbot) -> None:
    model = ScanResultsTableModel()
    row = _row("RELIANCE.NS", 82.5, 100.0, True)
    model.set_rows([row])

    assert model.row_at(0) is row
    assert model.row_at(5) is None


def test_data_returns_none_for_invalid_index(qtbot) -> None:
    model = ScanResultsTableModel()
    model.set_rows([_row("RELIANCE.NS", 82.5, 100.0, True)])

    assert model.data(QModelIndex()) is None
