import asyncio
from typing import Dict, List, Optional
import requests
from config import GOOGLE_BOOKS_API_URL, GOOGLE_BOOKS_API_KEY


async def search_books(query: str) -> List[Dict[str, str]]:
    """Search for books using Google Books API."""
    try:
        params = {
            "q": query,
            "maxResults": 5,
        }
        if GOOGLE_BOOKS_API_KEY:
            params["key"] = GOOGLE_BOOKS_API_KEY

        response = await asyncio.to_thread(
            requests.get,
            GOOGLE_BOOKS_API_URL,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            return []

        data = response.json()
        books: List[Dict[str, str]] = []

        for item in data.get("items", [])[:5]:
            info = item.get("volumeInfo", {})
            image_links = info.get("imageLinks", {})
            books.append({
                "title": info.get("title", "Нет названия"),
                "authors": ", ".join(info.get("authors", ["Неизвестно"])),
                "description": info.get("description", "Нет описания"),
                "link": info.get("infoLink") or info.get("previewLink") or item.get("selfLink", ""),
                "thumbnail": image_links.get("thumbnail", ""),
            })

        return books
    except Exception as e:
        print(f"Error searching books: {e}")
        return []


async def get_book_by_id(volume_id: str) -> Optional[Dict[str, str]]:
    """Get book details by volume ID using Google Books API."""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes/{volume_id}"
        params = {}
        if GOOGLE_BOOKS_API_KEY:
            params["key"] = GOOGLE_BOOKS_API_KEY

        response = await asyncio.to_thread(
            requests.get,
            url,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        info = data.get("volumeInfo", {})
        image_links = info.get("imageLinks", {})
        return {
            "title": info.get("title", "Нет названия"),
            "authors": ", ".join(info.get("authors", ["Неизвестно"])),
            "publisher": info.get("publisher", "Неизвестно"),
            "publishedDate": info.get("publishedDate", "Неизвестно"),
            "description": info.get("description", "Нет описания"),
            "pageCount": str(info.get("pageCount", "Неизвестно")),
            "language": info.get("language", "Неизвестно"),
            "link": info.get("infoLink") or info.get("canonicalVolumeLink") or data.get("selfLink", ""),
            "thumbnail": image_links.get("thumbnail", ""),
        }
    except Exception as e:
        print(f"Error getting book by ID: {e}")
        return None
