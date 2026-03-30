"""Prompt dialog for adding/editing prompts."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QFormLayout
)
from PySide6.QtCore import Signal


class PromptDialog(QDialog):
    """Dialog for adding or editing a prompt."""

    saved = Signal(dict)  # Emit dict with prompt data

    def __init__(self, categories, parent=None, prompt=None):
        super().__init__(parent)
        self.categories = categories
        self.prompt = prompt  # None for new prompt, dict for editing
        self._setup_ui()

        if prompt:
            self._populate_fields()

    def _setup_ui(self):
        self.setMinimumWidth(500)
        self.setWindowTitle("Add Prompt" if not self.prompt else "Edit Prompt")

        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(12)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter prompt title")
        form.addRow("Title:", self.title_input)

        # Content
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter prompt content...")
        self.content_input.setMinimumHeight(150)
        form.addRow("Content:", self.content_input)

        # Category
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("None", None)
        for cat in self.categories:
            self.category_combo.addItem(cat.name, cat.id)
        category_layout.addWidget(self.category_combo)
        form.addRow("Category:", category_layout)

        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("comma, separated, tags")
        form.addRow("Tags:", self.tags_input)

        layout.addLayout(form)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _populate_fields(self):
        """Populate fields when editing an existing prompt."""
        self.title_input.setText(self.prompt.title)
        self.content_input.setText(self.prompt.content)
        self.tags_input.setText(self.prompt.tags or "")

        # Set category
        if self.prompt.category_id is not None:
            index = self.category_combo.findData(self.prompt.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def _on_save(self):
        """Handle save button click."""
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not title:
            self.title_input.setFocus()
            return

        if not content:
            self.content_input.setFocus()
            return

        data = {
            "title": title,
            "content": content,
            "category_id": self.category_combo.currentData(),
            "tags": self.tags_input.text().strip() or None
        }

        self.saved.emit(data)
        self.accept()


class CategoryDialog(QDialog):
    """Simple dialog for adding a category."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Add Category")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Category name")
        form.addRow("Name:", self.name_input)
        layout.addLayout(form)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Add")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _on_save(self):
        name = self.name_input.text().strip()
        if name:
            self.accept()
        else:
            self.name_input.setFocus()

    def get_name(self) -> str:
        return self.name_input.text().strip()