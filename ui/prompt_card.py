"""Prompt card widget."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Signal, Qt
from datetime import datetime


class PromptCard(QFrame):
    """Individual prompt card widget displaying title, content preview, and tags."""

    clicked = Signal(int)  # Signal emits prompt_id
    edit_requested = Signal(int)  # Signal emits prompt_id
    delete_requested = Signal(int)  # Signal emits prompt_id
    copy_requested = Signal(int)  # Signal emits prompt_id

    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title
        self.title_label = QLabel(self.prompt.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Content preview (first 150 chars)
        content_preview = self.prompt.content[:150]
        if len(self.prompt.content) > 150:
            content_preview += "..."
        self.content_label = QLabel(content_preview)
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("color: #666;")
        layout.addWidget(self.content_label)

        # Tags
        if self.prompt.tags:
            self.tags_label = QLabel(f"Tags: {self.prompt.tags}")
            self.tags_label.setStyleSheet("color: #888; font-size: 11px;")
            layout.addWidget(self.tags_label)

        # Created date
        try:
            dt = datetime.fromisoformat(self.prompt.created_at.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            date_str = self.prompt.created_at

        self.date_label = QLabel(date_str)
        self.date_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.date_label)

        # Store prompt ID for click handling
        self.setProperty("prompt_id", self.prompt.id)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.prompt.id)
        super().mousePressEvent(event)