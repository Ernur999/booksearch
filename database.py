import sqlite3
from typing import Dict, List


class BookDatabase:
    """Database manager for book search history and library."""

    def __init__(self, db_path: str = "books.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self) -> None:
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    query TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    authors TEXT,
                    description TEXT,
                    link TEXT,
                    added_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_search(self, user_id: int, query: str) -> None:
        """Add search to history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO search_history (user_id, query) VALUES (?, ?)",
                (user_id, query),
            )

    def get_search_history(self, user_id: int, limit: int = 10) -> List[str]:
        """Get user's search history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT query FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit),
            )
            return [row[0] for row in cursor.fetchall()]

    def add_to_library(self, user_id: int, book: Dict) -> None:
        """Add book to user's library."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO user_library (user_id, title, authors, description, link)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    user_id,
                    book.get("title", ""),
                    book.get("authors", ""),
                    book.get("description", "")[:500],
                    book.get("link", ""),
                ),
            )

    def get_library(self, user_id: int) -> List[Dict]:
        """Get user's library."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, title, authors, description, link, added_date
                   FROM user_library WHERE user_id = ? ORDER BY added_date DESC""",
                (user_id,),
            )
            books: List[Dict] = []
            for row in cursor.fetchall():
                books.append(
                    {
                        "id": row[0],
                        "title": row[1],
                        "authors": row[2],
                        "description": row[3],
                        "link": row[4],
                        "added_date": row[5],
                    }
                )
            return books

    def remove_from_library(self, book_id: int, user_id: int) -> bool:
        """Remove book from library."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_library WHERE id = ? AND user_id = ?",
                (book_id, user_id),
            )
            return cursor.rowcount > 0

    def book_in_library(self, user_id: int, title: str, authors: str) -> bool:
        """Check if book already exists in library."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM user_library WHERE user_id = ? AND title = ? AND authors = ?",
                (user_id, title, authors),
            )
            return cursor.fetchone() is not None
