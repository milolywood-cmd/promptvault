# PromptVault — Local GUI Prompt Manager

## Stack
- Language: Python 3.11
- GUI: PySide6 (Qt for Python)
- Database: SQLite at ~/.local/share/promptvault/prompts.db
- No web server, no cloud, fully offline

## Rules
- Follow XDG base directory spec for all file paths
- Use Qt signals/slots for all UI logic
- Never hardcode paths — use pathlib
- All DB access through a dedicated db.py module
- Use QThread for any background work (never block the UI thread)

## Run
python main.py

## Test
pytest tests/