import asyncio
from typing import Dict, List
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
