from __future__ import annotations

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ai_screener.dashboard.controller import DashboardController
from ai_screener.dashboard.viewmodels.scan_results_model import ScanResultsTableModel
from ai_screener.dashboard.widgets.explanation_panel import ExplanationPanel
from ai_screener.scanner.rules import ScanStrategy


class MainWindow(QMainWindow):
    """The scan-results dashboard: a ranked table on the left, the
    selected symbol's "why selected" evidence on the right - matching
    the product's own mockup.

    All business logic lives in DashboardController; this class only
    wires Qt signals to controller calls and view-model updates.
    """

    def __init__(
        self,
        controller: DashboardController,
        universe: list[str],
        strategy: ScanStrategy,
        asset_type: str = "equity",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._controller = controller
        self._universe = universe
        self._strategy = strategy
        self._asset_type = asset_type

        self.setWindowTitle("AI Screener")

        self._model = ScanResultsTableModel()
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.selectionModel().currentRowChanged.connect(self._on_row_selected)

        self._explanation_panel = ExplanationPanel()

        self._status_label = QLabel(
            f"Strategy: {strategy.name}. Press “Run Scan” to begin."
        )
        self._status_label.setWordWrap(True)

        self._scan_button = QPushButton("Run Scan")
        self._scan_button.clicked.connect(self._on_run_scan_clicked)

        results_column = QVBoxLayout()
        results_column.addWidget(self._scan_button)
        results_column.addWidget(self._status_label)
        results_column.addWidget(self._table)
        results_widget = QWidget()
        results_widget.setLayout(results_column)

        central_layout = QHBoxLayout()
        central_layout.addWidget(results_widget, 2)
        central_layout.addWidget(self._explanation_panel, 1)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def run_scan(self) -> None:
        """Run the configured strategy over the configured universe and
        refresh the table. Exposed as a plain method (not just the
        button's click handler) so tests can trigger a scan directly."""

        rows = self._controller.run_scan(
            self._universe, self._strategy, self._asset_type
        )
        self._model.set_rows(rows)
        self._explanation_panel.clear()

        if not rows:
            self._status_label.setText("No symbols passed the scan.")
            return

        gate_note = (
            "" if rows[0].is_backtested else " (strategy has not been backtested yet)"
        )
        self._status_label.setText(f"{len(rows)} symbol(s) passed.{gate_note}")

    def _on_run_scan_clicked(self) -> None:
        self.run_scan()

    def _on_row_selected(self, current: QModelIndex, previous: QModelIndex) -> None:
        if not current.isValid():
            self._explanation_panel.clear()
            return

        row = self._model.row_at(current.row())

        if row is None:
            self._explanation_panel.clear()
            return

        self._explanation_panel.show_explanation(
            row.ranked_result.symbol, row.explanation
        )
