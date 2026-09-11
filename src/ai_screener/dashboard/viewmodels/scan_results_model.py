from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
)

from ai_screener.dashboard.controller import DashboardRow

_COLUMNS = ("Symbol", "Score", "Confidence", "Backtested")


class ScanResultsTableModel(QAbstractTableModel):
    """Thin Qt adapter over a list[DashboardRow].

    Holds no business logic of its own - DashboardController produces
    the rows, this model only knows how to present them as a table.
    """

    def __init__(
        self, rows: list[DashboardRow] | None = None, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._rows: list[DashboardRow] = rows or []

    def set_rows(self, rows: list[DashboardRow]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def row_at(self, row_index: int) -> DashboardRow | None:
        if 0 <= row_index < len(self._rows):
            return self._rows[row_index]
        return None

    def rowCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),  # noqa: B008
    ) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),  # noqa: B008
    ) -> int:
        return 0 if parent.isValid() else len(_COLUMNS)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return _COLUMNS[section]
        return None

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        row = self._rows[index.row()]
        column = index.column()

        if column == 0:
            return row.ranked_result.symbol
        if column == 1:
            return f"{row.ranked_result.score:.1f}"
        if column == 2:
            return f"{row.ranked_result.confidence:.0f}%"
        if column == 3:
            return "Yes" if row.is_backtested else "No"
        return None
