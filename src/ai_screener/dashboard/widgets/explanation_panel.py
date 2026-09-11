from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from ai_screener.explainability.models import Explanation

_PLACEHOLDER_TEXT = "Select a symbol to see why it was selected."


class ExplanationPanel(QWidget):
    """Renders one symbol's Explanation as the "why selected" checklist
    from the product's own mockup: a title with the confidence score,
    then one line per supporting Reason."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._title = QLabel(_PLACEHOLDER_TEXT)
        self._title.setWordWrap(True)

        self._reason_list = QListWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._reason_list)

    def show_explanation(self, symbol: str, explanation: Explanation) -> None:
        self._title.setText(
            f"Why {symbol} was selected " f"(confidence: {explanation.confidence:.0f}%)"
        )

        self._reason_list.clear()

        if not explanation.reasons:
            self._reason_list.addItem(
                QListWidgetItem("No supporting evidence available yet.")
            )
            return

        for reason in explanation.reasons:
            self._reason_list.addItem(
                QListWidgetItem(f"[{reason.category}] {reason.statement}")
            )

    def clear(self) -> None:
        self._title.setText(_PLACEHOLDER_TEXT)
        self._reason_list.clear()
