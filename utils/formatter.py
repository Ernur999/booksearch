def format_books(books):
    """Format books list for Telegram message."""
    if not books:
        return "❌ Ничего не найдено"

    result = ""

    for book in books:
        result += f"📚 <b>{book['title']}</b>\n"
        result += f"✍️ <i>{book['authors']}</i>\n"

        description = book.get("description", "Нет описания")
        if len(description) > 200:
            description = description[:200].rstrip() + "..."

        result += f"📖 {description}\n"

        if book.get("link"):
            result += f"🔗 <a href='{book['link']}'>Подробнее</a>\n"

        result += "\n"

    return result


def format_book_detailed(book, index, total):
    """Format single book with pagination."""
    result = f"📚 <b>{book['title']}</b>\n"
    result += f"✍️ <i>{book['authors']}</i>\n\n"

    description = book.get("description", "Нет описания")
    if len(description) > 500:
        description = description[:500].rstrip() + "..."

    result += f"📖 <i>Описание:</i>\n{description}\n\n"

    if book.get("thumbnail"):
        result += f"🖼 <a href='{book['thumbnail']}'>Обложка</a>\n"
    if book.get("link"):
        result += f"🔗 <a href='{book['link']}'>Посмотреть полное описание</a>\n\n"
    else:
        result += "\n"

    result += f"📍 Книга {index + 1} из {total}"
    return result


def format_volume_by_id(book: dict) -> str:
    """Format detailed book info retrieved by volume ID."""
    result = f"📚 <b>{book['title']}</b>\n"
    result += f"✍️ <i>{book['authors']}</i>\n\n"

    if book.get("publisher") and book["publisher"] != "Неизвестно":
        result += f"🏢 <b>Издатель:</b> {book['publisher']}\n"
    if book.get("publishedDate") and book["publishedDate"] != "Неизвестно":
        result += f"📅 <b>Дата публикации:</b> {book['publishedDate']}\n"
    if book.get("pageCount") and book["pageCount"] != "Неизвестно":
        result += f"📄 <b>Страниц:</b> {book['pageCount']}\n"
    if book.get("language") and book["language"] != "Неизвестно":
        result += f"🌐 <b>Язык:</b> {book['language']}\n"

    result += "\n"

    description = book.get("description", "Нет описания")
    if len(description) > 700:
        description = description[:700].rstrip() + "..."
    result += f"📖 <i>Описание:</i>\n{description}\n\n"

    if book.get("thumbnail"):
        result += f"🖼 <a href='{book['thumbnail']}'>Обложка</a>\n"
    if book.get("link"):
        result += f"🔗 <a href='{book['link']}'>Открыть в Google Книгах</a>\n"

    return result
