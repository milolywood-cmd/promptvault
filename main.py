"""PromptVault - Local GUI Prompt Manager."""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

import db
from ui.main_window import MainWindow


def main():
    """Application entry point."""
    # Initialize database
    db.init_db()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("PromptVault")
    app.setApplicationVersion("1.0.0")

    # Set style
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()