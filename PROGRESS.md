# PromptVault Progress

## Summary

A local GUI prompt manager built with PySide6 and SQLite, designed for offline use.

## What's Built

| Component | Status |
|-----------|--------|
| `db.py` - SQLite database module | ✅ Complete |
| `main.py` - Application entry point | ✅ Complete |
| `ui/sidebar.py` - Category list | ✅ Complete |
| `ui/search_bar.py` - Search input | ✅ Complete |
| `ui/prompt_card.py` - Card widget | ✅ Complete |
| `ui/prompt_dialog.py` - Add/Edit dialogs | ✅ Complete |
| `ui/main_window.py` - Main window | ✅ Complete |
| `tests/test_db.py` - Database tests | ✅ 10/10 passing |
| `requirements.txt` - Dependencies | ✅ Complete |

## What's Working

- Categories: add, select, view all
- Prompts: add, edit, delete, copy to clipboard
- Search: filters by title, content, and tags
- Database: SQLite at `~/.local/share/promptvault/prompts.db`
- XDG compliance: uses pathlib, follows spec
- Background threads: QThread for DB operations
- UI: Sidebar + card layout with button bar

## Not Done / Gaps

- **No context menu on cards** — can't right-click to edit/delete/copy directly
- **No GUI tests** — only database unit tests exist
- **Not tested with display** — imports work but haven't run with a visible window

## Next Step

Run the app with a display to verify the full GUI works:

```bash
python3 main.py
```