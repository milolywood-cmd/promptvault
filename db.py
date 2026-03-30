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