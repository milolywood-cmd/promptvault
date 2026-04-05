"""Main window for PromptVault."""
import db
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGridLayout, QPushButton, QMessageBox,
    QSplitter, QStatusBar, QLabel, QFileDialog
)
from PySide6.QtCore import Signal, QThread, Qt
from PySide6.QtGui import QClipboard

from .search_bar import SearchBar
from .sidebar import Sidebar
from .prompt_card import PromptCard
from .prompt_dialog import PromptDialog, CategoryDialog


class LoadPromptsThread(QThread):
    """Background thread for loading prompts from database."""

    finished = Signal(list)

    def __init__(self, category_id=None, search=None):
        super().__init__()
        self.category_id = category_id
        self.search = search

    def run(self):
        prompts = db.get_prompts(self.category_id, self.search)
        self.finished.emit(prompts)


class LoadCategoriesThread(QThread):
    """Background thread for loading categories."""

    finished = Signal(list)

    def run(self):
        categories = db.get_categories()
        self.finished.emit(categories)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.current_category_id = None
        self.current_search = ""
        self.load_threads = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("PromptVault")
        self.setMinimumSize(900, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Splitter for sidebar and content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.category_selected.connect(self._on_category_selected)
        self.sidebar.add_category_clicked.connect(self._on_add_category)
        splitter.addWidget(self.sidebar)

        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # Search bar
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._on_search_changed)
        content_layout.addWidget(self.search_bar)

        # Button bar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.add_btn = QPushButton("+ Add New Prompt")
        self.add_btn.clicked.connect(self._on_add_prompt)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit_prompt)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete_prompt)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self._on_copy_clipboard)
        self.copy_btn.setEnabled(False)
        button_layout.addWidget(self.copy_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self._on_export)
        button_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self._on_import)
        button_layout.addWidget(self.import_btn)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Prompt cards area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignTop)

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.cards_container)
        content_layout.addWidget(scroll)

        splitter.addWidget(content_widget)
        splitter.setSizes([200, 700])

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Selected prompt tracking
        self.selected_prompt_id = None

    def _load_data(self):
        """Load categories and prompts."""
        # Load categories in background
        self._load_categories()

        # Load prompts in background
        self._load_prompts()

    def _load_categories(self):
        """Load categories from database in background thread."""
        thread = LoadCategoriesThread()
        thread.finished.connect(self._on_categories_loaded)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        self.load_threads.append(thread)

    def _load_prompts(self):
        """Load prompts from database in background thread."""
        thread = LoadPromptsThread(self.current_category_id, self.current_search)
        thread.finished.connect(self._on_prompts_loaded)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        self.load_threads.append(thread)
        self.status_label.setText("Loading...")

    def _on_categories_loaded(self, categories):
        """Handle categories loaded."""
        self.sidebar.load_categories(categories)

    def _on_prompts_loaded(self, prompts):
        """Handle prompts loaded."""
        self._display_prompts(prompts)
        self.status_label.setText(f"{len(prompts)} prompt(s)")

    def _display_prompts(self, prompts):
        """Display prompts as cards."""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new cards
        columns = 2
        for i, prompt in enumerate(prompts):
            row = i // columns
            col = i % columns

            card = PromptCard(prompt)
            card.clicked.connect(self._on_prompt_clicked)
            card.edit_requested.connect(self._on_edit_prompt_from_card)
            card.delete_requested.connect(self._on_delete_prompt_from_card)
            card.copy_requested.connect(self._on_copy_from_card)

            self.cards_layout.addWidget(card, row, col)

    def _on_category_selected(self, category_id):
        """Handle category selection."""
        self.current_category_id = category_id
        self.selected_prompt_id = None
        self._update_button_states()
        self._load_prompts()

    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.current_search = text
        self.selected_prompt_id = None
        self._update_button_states()
        self._load_prompts()

    def _on_prompt_clicked(self, prompt_id):
        """Handle prompt card click."""
        self.selected_prompt_id = prompt_id
        self._update_button_states()

    def _on_edit_prompt_from_card(self, prompt_id):
        """Handle edit request from card."""
        self.selected_prompt_id = prompt_id
        self._on_edit_prompt()

    def _on_delete_prompt_from_card(self, prompt_id):
        """Handle delete request from card."""
        self.selected_prompt_id = prompt_id
        self._on_delete_prompt()

    def _on_copy_from_card(self, prompt_id):
        """Handle copy request from card."""
        self.selected_prompt_id = prompt_id
        self._on_copy_clipboard()

    def _update_button_states(self):
        """Update button enabled states based on selection."""
        has_selection = self.selected_prompt_id is not None
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.copy_btn.setEnabled(has_selection)

    def _on_add_prompt(self):
        """Handle add prompt button click."""
        categories = db.get_categories()
        dialog = PromptDialog(categories, self)
        dialog.saved.connect(self._save_new_prompt)
        dialog.exec()

    def _save_new_prompt(self, data):
        """Save a new prompt."""
        prompt = db.add_prompt(
            data["title"],
            data["content"],
            data["category_id"],
            data["tags"]
        )
        self._load_prompts()
        self.status_label.setText(f"Added: {prompt.title}")

    def _on_edit_prompt(self):
        """Handle edit button click."""
        if not self.selected_prompt_id:
            return

        prompts = db.get_prompts()
        prompt = next((p for p in prompts if p.id == self.selected_prompt_id), None)
        if not prompt:
            return

        categories = db.get_categories()
        dialog = PromptDialog(categories, self, prompt=prompt)
        dialog.saved.connect(lambda data: self._save_edited_prompt(prompt.id, data))
        dialog.exec()

    def _save_edited_prompt(self, prompt_id, data):
        """Save edited prompt."""
        db.update_prompt(
            prompt_id,
            data["title"],
            data["content"],
            data["category_id"],
            data["tags"]
        )
        self._load_prompts()
        self.status_label.setText(f"Updated: {data['title']}")

    def _on_delete_prompt(self):
        """Handle delete button click."""
        if not self.selected_prompt_id:
            return

        reply = QMessageBox.question(
            self,
            "Delete Prompt",
            "Are you sure you want to delete this prompt?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            prompt = db.delete_prompt(self.selected_prompt_id)
            self.selected_prompt_id = None
            self._update_button_states()
            self._load_prompts()
            self.status_label.setText("Prompt deleted")

    def _on_copy_clipboard(self):
        """Handle copy to clipboard button click."""
        if not self.selected_prompt_id:
            return

        prompts = db.get_prompts()
        prompt = next((p for p in prompts if p.id == self.selected_prompt_id), None)
        if not prompt:
            return

        clipboard = QClipboard()
        clipboard.setText(prompt.content)
        self.status_label.setText(f"Copied: {prompt.title}")

    def _on_add_category(self):
        """Handle add category button click."""
        dialog = CategoryDialog(self)
        if dialog.exec():
            name = dialog.get_name()
            try:
                db.add_category(name)
                self._load_categories()
                self.status_label.setText(f"Added category: {name}")
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not add category: {str(e)}"
                )

    def _on_export(self):
        """Handle export button click."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Prompts",
            "prompts_export.md",
            "Markdown Files (*.md);;All Files (*)"
        )

        if not file_path:
            return

        try:
            path = Path(file_path)
            count = db.export_prompts(path)
            self.status_label.setText(f"Exported {count} prompt(s) to {path.name}")
            QMessageBox.information(
                self,
                "Export Complete",
                f"Successfully exported {count} prompt(s) to:\n{path}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Error",
                f"Could not export prompts: {str(e)}"
            )

    def _on_import(self):
        """Handle import button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Prompts",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )

        if not file_path:
            return

        reply = QMessageBox.question(
            self,
            "Import Prompts",
            "This will import prompts from the file. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            path = Path(file_path)
            imported, errors = db.import_prompts(path)
            self._load_prompts()
            self._load_categories()
            self.status_label.setText(f"Imported {imported} prompt(s)")
            QMessageBox.information(
                self,
                "Import Complete",
                f"Imported: {imported} prompt(s)\nErrors: {errors}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Import Error",
                f"Could not import prompts: {str(e)}"
            )