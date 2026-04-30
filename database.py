import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class BookDatabase:
    """Database manager for book search history and library"""
    
    def __init__(self, db_path: str = "books.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User library table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                authors TEXT,
                description TEXT,
                link TEXT,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_search(self, user_id: int, query: str) -> None:
        """Add search to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_history (user_id, query) VALUES (?, ?)",
            (user_id, query)
        )
        conn.commit()
        conn.close()
    
    def get_search_history(self, user_id: int, limit: int = 10) -> List[str]:
        """Get user's search history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT query FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        queries = [row[0] for row in cursor.fetchall()]
        conn.close()
        return queries
    
    def add_to_library(self, user_id: int, book: Dict) -> None:
        """Add book to user's library"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO user_library (user_id, title, authors, description, link) 
               VALUES (?, ?, ?, ?, ?)""",
            (
                user_id,
                book.get('title', ''),
                book.get('authors', ''),
                book.get('description', '')[:500],
                book.get('link', '')
            )
        )
        conn.commit()
        conn.close()
    
    def get_library(self, user_id: int) -> List[Dict]:
        """Get user's library"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, title, authors, description, link, added_date 
               FROM user_library WHERE user_id = ? ORDER BY added_date DESC""",
            (user_id,)
        )
        books = []
        for row in cursor.fetchall():
            books.append({
                'id': row[0],
                'title': row[1],
                'authors': row[2],
                'description': row[3],
                'link': row[4],
                'added_date': row[5]
            })
        conn.close()
        return books
    
    def remove_from_library(self, book_id: int, user_id: int) -> bool:
        """Remove book from library"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user_library WHERE id = ? AND user_id = ?",
            (book_id, user_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    def book_in_library(self, user_id: int, title: str) -> bool:
        """Check if book already in library"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM user_library WHERE user_id = ? AND title = ?",
            (user_id, title)
        )
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
