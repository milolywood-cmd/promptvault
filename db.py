"""Database module for PromptVault."""
import sqlite3
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

# XDG base directory spec
DATA_DIR = Path.home() / ".local" / "share" / "promptvault"
DB_PATH = DATA_DIR / "prompts.db"


def _get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


def init_db() -> None:
    """Initialize database and create tables if they don't exist."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category_id INTEGER,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


@dataclass
class Category:
    id: int
    name: str


@dataclass
class Prompt:
    id: int
    title: str
    content: str
    category_id: Optional[int]
    tags: Optional[str]
    created_at: str


def get_categories() -> list[Category]:
    """Fetch all categories ordered by name."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        return [Category(id=row["id"], name=row["name"]) for row in cursor.fetchall()]
    finally:
        conn.close()


def add_category(name: str) -> Category:
    """Add a new category and return it."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        category_id = cursor.lastrowid
        return Category(id=category_id, name=name)
    finally:
        conn.close()


def delete_category(category_id: int) -> None:
    """Delete a category by ID."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
    finally:
        conn.close()


def get_prompts(category_id: Optional[int] = None, search: Optional[str] = None) -> list[Prompt]:
    """Fetch prompts with optional category and search filters."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, title, content, category_id, tags, created_at FROM prompts WHERE 1=1"
        params = []

        if category_id is not None:
            query += " AND category_id = ?"
            params.append(category_id)

        if search:
            query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        return [
            Prompt(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                category_id=row["category_id"],
                tags=row["tags"],
                created_at=row["created_at"]
            )
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()


def add_prompt(title: str, content: str, category_id: Optional[int], tags: Optional[str]) -> Prompt:
    """Add a new prompt and return it."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO prompts (title, content, category_id, tags) VALUES (?, ?, ?, ?)",
            (title, content, category_id, tags)
        )
        conn.commit()
        prompt_id = cursor.lastrowid
        cursor.execute("SELECT created_at FROM prompts WHERE id = ?", (prompt_id,))
        created_at = cursor.fetchone()["created_at"]
        return Prompt(
            id=prompt_id,
            title=title,
            content=content,
            category_id=category_id,
            tags=tags,
            created_at=created_at
        )
    finally:
        conn.close()


def update_prompt(prompt_id: int, title: str, content: str, category_id: Optional[int], tags: Optional[str]) -> None:
    """Update an existing prompt."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE prompts SET title = ?, content = ?, category_id = ?, tags = ? WHERE id = ?",
            (title, content, category_id, tags, prompt_id)
        )
        conn.commit()
    finally:
        conn.close()


def delete_prompt(prompt_id: int) -> None:
    """Delete a prompt by ID."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        conn.commit()
    finally:
        conn.close()


def get_category_name(category_id: int) -> Optional[str]:
    """Get category name by ID."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return row["name"] if row else None
    finally:
        conn.close()


def export_prompts(path: Path) -> int:
    """Export all prompts to a human-readable markdown file.

    Returns the number of prompts exported.
    """
    prompts = get_prompts()
    categories = {c.id: c.name for c in get_categories()}

    lines = [
        "# PromptVault Export",
        f"# Exported: 2026-04-04",
        f"# Total prompts: {len(prompts)}",
        "",
    ]

    for prompt in prompts:
        lines.append("---")
        lines.append(f"title: {prompt.title}")
        if prompt.category_id and prompt.category_id in categories:
            lines.append(f"category: {categories[prompt.category_id]}")
        if prompt.tags:
            lines.append(f"tags: {prompt.tags}")
        lines.append("---")
        lines.append("")
        lines.append(prompt.content)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return len(prompts)


def import_prompts(path: Path) -> tuple[int, int]:
    """Import prompts from a human-readable markdown file.

    Returns (imported_count, errors_count).
    """
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    categories = {c.name.lower(): c.id for c in get_categories()}
    category_cache = {}  # cache for newly created categories

    imported = 0
    errors = 0

    # Parse prompts separated by "---"
    current_prompt = None
    in_content = False
    content_lines = []

    for line in lines:
        line = line.rstrip()

        # Skip comments and headers
        if line.startswith("#") and not line.startswith("---"):
            continue

        if line == "---":
            if current_prompt is not None:
                # Save previous prompt
                if content_lines:
                    current_prompt["content"] = "\n".join(content_lines).strip()
                    try:
                        _import_single_prompt(current_prompt, categories, category_cache)
                        imported += 1
                    except Exception:
                        errors += 1
                content_lines = []
                current_prompt = None
                in_content = False
            else:
                # Start new prompt
                current_prompt = {"title": None, "category": None, "tags": None, "content": ""}
                in_content = False
        elif current_prompt is not None:
            if not in_content:
                # Still in header
                if line.startswith("title:"):
                    current_prompt["title"] = line[6:].strip()
                elif line.startswith("category:"):
                    current_prompt["category"] = line[9:].strip()
                elif line.startswith("tags:"):
                    current_prompt["tags"] = line[5:].strip()
                elif line == "":
                    # Empty line after header = content starts
                    in_content = True
            else:
                # In content
                content_lines.append(line)

    # Don't forget the last prompt
    if current_prompt is not None and content_lines:
        current_prompt["content"] = "\n".join(content_lines).strip()
        try:
            _import_single_prompt(current_prompt, categories, category_cache)
            imported += 1
        except Exception:
            errors += 1

    return imported, errors


def _import_single_prompt(prompt_data, categories, category_cache):
    """Import a single prompt, creating category if needed."""
    title = prompt_data.get("title")
    content = prompt_data.get("content", "")

    if not title or not content:
        raise ValueError("Missing title or content")

    # Resolve category
    category_id = None
    category_name = prompt_data.get("category")
    if category_name:
        cat_lower = category_name.lower()
        if cat_lower in categories:
            category_id = categories[cat_lower]
        elif cat_lower in category_cache:
            category_id = category_cache[cat_lower]
        else:
            # Create new category
            new_cat = add_category(category_name)
            categories[cat_lower] = new_cat.id
            category_cache[cat_lower] = new_cat.id
            category_id = new_cat.id

    add_prompt(title, content, category_id, prompt_data.get("tags"))