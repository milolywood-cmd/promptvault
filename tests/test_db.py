"""Tests for the database module."""
import pytest
import tempfile
import os
from pathlib import Path

# Mock the database path for testing
import db


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Use a temporary database for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        monkeypatch.setattr(db, "DB_PATH", test_db_path)
        db.init_db()
        yield test_db_path


def test_get_categories_empty():
    """Test getting categories when none exist."""
    categories = db.get_categories()
    assert categories == []


def test_add_category():
    """Test adding a category."""
    cat = db.add_category("Test Category")
    assert cat.name == "Test Category"
    assert cat.id is not None

    # Verify it's in the list
    categories = db.get_categories()
    assert len(categories) == 1
    assert categories[0].name == "Test Category"


def test_add_duplicate_category():
    """Test adding a duplicate category raises error."""
    db.add_category("Duplicate")

    with pytest.raises(Exception):
        db.add_category("Duplicate")


def test_get_prompts_empty():
    """Test getting prompts when none exist."""
    prompts = db.get_prompts()
    assert prompts == []


def test_add_prompt():
    """Test adding a prompt."""
    cat = db.add_category("Work")
    prompt = db.add_prompt(
        title="Test Prompt",
        content="This is test content",
        category_id=cat.id,
        tags="test, sample"
    )

    assert prompt.title == "Test Prompt"
    assert prompt.content == "This is test content"
    assert prompt.category_id == cat.id
    assert prompt.tags == "test, sample"


def test_get_prompts_with_category():
    """Test getting prompts filtered by category."""
    cat = db.add_category("Personal")
    db.add_prompt("Prompt 1", "Content 1", cat.id, None)
    db.add_prompt("Prompt 2", "Content 2", None, None)

    # Get all
    all_prompts = db.get_prompts()
    assert len(all_prompts) == 2

    # Get filtered by category
    filtered = db.get_prompts(category_id=cat.id)
    assert len(filtered) == 1
    assert filtered[0].title == "Prompt 1"


def test_search_prompts():
    """Test searching prompts."""
    db.add_prompt("Python Script", "Print hello world", None, "python")
    db.add_prompt("Java Code", "System.out.println", None, "java")

    # Search by title
    results = db.get_prompts(search="Python")
    assert len(results) == 1
    assert results[0].title == "Python Script"

    # Search by content
    results = db.get_prompts(search="hello")
    assert len(results) == 1
    assert results[0].title == "Python Script"

    # Search by tags
    results = db.get_prompts(search="java")
    assert len(results) == 1
    assert results[0].title == "Java Code"


def test_update_prompt():
    """Test updating a prompt."""
    prompt = db.add_prompt("Original", "Original content", None, "original")

    db.update_prompt(prompt.id, "Updated", "New content", None, "updated")

    prompts = db.get_prompts()
    assert len(prompts) == 1
    assert prompts[0].title == "Updated"
    assert prompts[0].content == "New content"
    assert prompts[0].tags == "updated"


def test_delete_prompt():
    """Test deleting a prompt."""
    prompt = db.add_prompt("To Delete", "Content", None, None)

    prompts = db.get_prompts()
    assert len(prompts) == 1

    db.delete_prompt(prompt.id)

    prompts = db.get_prompts()
    assert len(prompts) == 0


def test_delete_category_does_not_delete_prompts():
    """Test that deleting a category sets prompt category_id to NULL."""
    cat = db.add_category("To Delete")
    db.add_prompt("My Prompt", "Content", cat.id, None)

    db.delete_category(cat.id)

    prompts = db.get_prompts()
    assert len(prompts) == 1
    assert prompts[0].category_id is None