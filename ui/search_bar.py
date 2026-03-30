"""Search bar widget."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit
from PySide6.QtCore import Signal


class SearchBar(QWidget):
    """Search input widget with signal for search changes."""

    search_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search prompts...")
        self.search_input.textChanged.connect(self._on_text_changed)

        layout.addWidget(self.search_input)

    def _on_text_changed(self, text: str):
        self.search_changed.emit(text)

    def text(self) -> str:
        return self.search_input.text()

    def clear(self):
        self.search_input.clear()