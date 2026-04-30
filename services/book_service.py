import requests
from config import GOOGLE_BOOKS_API_URL


def search_books(query):
    """Search for books using Google Books API"""
    try:
        url = f"{GOOGLE_BOOKS_API_URL}?q={query}"
        response = requests.get(url)

        if response.status_code != 200:
            return []

        data = response.json()
        books = []

        for item in data.get("items", [])[:5]:
            info = item.get("volumeInfo", {})

            books.append({
                "title": info.get("title", "Нет названия"),
                "authors": ", ".join(info.get("authors", ["Неизвестно"])),
                "description": info.get("description", "Нет описания"),
                "link": item.get("selfLink", "")
            })

        return books
    except Exception as e:
        print(f"Error searching books: {e}")
        return []
