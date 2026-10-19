"""SQLite database operations."""

import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from bookmarks.config import DB_PATH
from bookmarks.models import Bookmark


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                tags TEXT,
                category TEXT,
                description TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def add_bookmark(title: str, url: str, tags: str = "", category: str = "", description: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO bookmarks (title, url, tags, category, description) VALUES (?, ?, ?, ?, ?)",
            (title, url, tags, category, description),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_bookmarks() -> List[Bookmark]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM bookmarks ORDER BY title").fetchall()
        return [_row_to_bookmark(r) for r in rows]


def get_bookmark_by_id(bookmark_id: int) -> Optional[Bookmark]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,)).fetchone()
        return _row_to_bookmark(row) if row else None


def search_bookmarks(query: str) -> List[Bookmark]:
    q = f"%{query}%"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM bookmarks
            WHERE title LIKE ? OR url LIKE ? OR tags LIKE ? OR category LIKE ? OR description LIKE ?
            ORDER BY title
            """,
            (q, q, q, q, q),
        ).fetchall()
        return [_row_to_bookmark(r) for r in rows]


def delete_bookmark(bookmark_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        conn.commit()
        return cursor.rowcount > 0


def _row_to_bookmark(row: sqlite3.Row) -> Bookmark:
    return Bookmark(
        id=row["id"],
        title=row["title"],
        url=row["url"],
        tags=row["tags"] or "",
        category=row["category"] or "",
        description=row["description"] or "",
    )
