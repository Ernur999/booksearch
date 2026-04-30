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

    if book.get("link"):
        result += f"🔗 <a href='{book['link']}'>Посмотреть полное описание</a>\n\n"

    result += f"📍 Книга {index + 1} из {total}"
    return result
