"""Sidebar widget for categories."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel
from PySide6.QtCore import Signal


class Sidebar(QWidget):
    """Category list widget with add category button."""

    category_selected = Signal(int)  # None for "All", category_id for specific category
    add_category_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title
        title = QLabel("Categories")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Category list
        self.category_list = QListWidget()
        self.category_list.setMinimumWidth(180)
        self.category_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.category_list)

        # Add category button
        self.add_category_btn = QPushButton("+ Add Category")
        self.add_category_btn.clicked.connect(self.add_category_clicked.emit)
        layout.addWidget(self.add_category_btn)

    def _on_item_clicked(self, item):
        category_id = item.data(Qt.UserRole)
        self.category_selected.emit(category_id)

    def load_categories(self, categories):
        """Load categories into the list."""
        self.category_list.clear()

        # Add "All" option
        all_item = QListWidgetItem("All Prompts")
        all_item.setData(Qt.UserRole, None)
        self.category_list.addItem(all_item)

        # Add categories
        for cat in categories:
            item = QListWidgetItem(cat.name)
            item.setData(Qt.UserRole, cat.id)
            self.category_list.addItem(item)

    def select_all(self):
        """Select the 'All' category."""
        self.category_list.setCurrentRow(0)