# PromptVault

A local GUI application for managing AI prompts, built with PySide6.

## Features

- **Local Storage** — All prompts stored locally in SQLite, no cloud required
- **Categories** — Organize prompts into categories
- **Search** — Full-text search across titles, content, and tags
- **Tagging** — Add tags for better organization
- **Offline** — Works completely offline, no internet required

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/milolywood-cmd/promptvault.git
cd promptvault

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### From Debian Package

```bash
sudo dpkg -i promptvault_1.0.0_all.deb
sudo apt install -f  # Install any missing dependencies
```

## Requirements

- Python 3.11+
- PySide6 >= 6.5.0

## Usage

1. Launch PromptVault: `python main.py`
2. Add categories using the sidebar
3. Add prompts with the + button
4. Search using the search bar
5. Click a prompt to view/edit

## Data Location

- Database: `~/.local/share/promptvault/prompts.db`

## Development

```bash
# Run tests
pytest tests/
```

## License

MIT