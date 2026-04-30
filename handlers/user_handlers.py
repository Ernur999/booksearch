from aiogram import types, F, Router
from aiogram.filters import Command
from services.book_service import search_books
from utils.formatter import format_books, format_book_detailed
from database import BookDatabase
from keyboards import (
    get_main_keyboard,
    get_book_keyboards,
    get_library_keyboard,
    get_library_book_keyboard,
    get_library_overview_keyboard,
    get_history_keyboard,
)

router = Router()
db = BookDatabase()

# Store current search results per user
user_search_results = {}


@router.message(Command("start"))
async def handle_start(message: types.Message):
    """Handle /start command"""
    await message.answer(
        "👋 Привет! Я бот для поиска книг.\n\n"
        "Просто напиши название книги, и я найду её для тебя! 📚\n\n"
        "Команды:\n"
        "/start - начало\n"
        "/help - справка",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Handle /help command"""
    await message.answer(
        "📖 Как использовать бота:\n\n"
        "1. Напиши название книги (например: 'Harry Potter')\n"
        "2. Я найду книги в Google Books API\n"
        "3. Выбери книги для добавления в библиотеку\n\n"
        "💾 Функции:\n"
        "📚 Моя библиотека - просмотр сохранённых книг\n"
        "🔍 История поисков - твои последние поиски\n"
        "❌ История последних - удаление последней книги\n\n"
        "Команды:\n"
        "/start - начало\n"
        "/help - справка",
        reply_markup=get_main_keyboard()
    )


def format_library_text(books):
    text = f"📚 Твоя библиотека ({len(books)} книг):\n\n"
    for i, book in enumerate(books, 1):
        text += f"{i}. 📖 <b>{book['title']}</b>\n"
        text += f"   ✍️ {book['authors']}\n"
        if book.get("added_date"):
            text += f"   📅 Добавлено: {book['added_date'][:10]}\n"
        text += "\n"
    return text


@router.message(F.text == "📚 Моя библиотека")
async def show_library(message: types.Message):
    """Show user's library."""
    user_id = message.from_user.id
    books = db.get_library(user_id)

    if not books:
        await message.answer(
            "📚 Твоя библиотека пуста!\n\n"
            "Поищи книги и добавь их в библиотеку 📖",
            reply_markup=get_main_keyboard(),
        )
        return

    await message.answer(
        format_library_text(books),
        parse_mode="HTML",
        reply_markup=get_library_overview_keyboard(books),
    )


@router.message(F.text == "🔍 История поисков")
async def show_search_history(message: types.Message):
    """Show search history"""
    user_id = message.from_user.id
    history = db.get_search_history(user_id, limit=10)
    
    if not history:
        await message.answer(
            "🔍 История поисков пуста!",
            reply_markup=get_main_keyboard()
        )
        return
    
    text = "🔍 Твоя история поисков:\n\n"
    for i, query in enumerate(history, 1):
        text += f"{i}. {query}\n"
    
    text += "\n📝 Напиши одно из этих слов для повторного поиска"
    await message.answer(text, reply_markup=get_history_keyboard())


@router.message(F.text == "❌ История последних")
async def show_last_books(message: types.Message):
    """Show last added books"""
    user_id = message.from_user.id
    books = db.get_library(user_id)
    
    if not books:
        await message.answer(
            "❌ Нет добавленных книг!",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Show last 5 books
    recent = books[:5]
    text = "❌ Недавно добавленные:\n\n"
    
    for i, book in enumerate(recent, 1):
        text += f"{i}. 📖 <b>{book['title']}</b>\n"
        text += f"   ✍️ {book['authors']}\n\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_library_keyboard())


@router.message(F.text == "ℹ️ Справка")
async def show_info(message: types.Message):
    """Show bot info"""
    await message.answer(
        "ℹ️ <b>О боте</b>\n\n"
        "🤖 Telegram Bot для поиска книг\n"
        "📚 Используется Google Books API\n"
        "💾 Все книги сохраняются в локальную БД\n\n"
        "<b>Возможности:</b>\n"
        "✅ Поиск книг по названию\n"
        "✅ Сохранение в личную библиотеку\n"
        "✅ История поисков\n"
        "✅ Просмотр и удаление книг\n\n"
        "🚀 Начни с поиска!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


@router.message()
async def handle_message(message: types.Message):
    """Handle text messages with book search."""
    user_id = message.from_user.id
    query = message.text.strip()

    if not query:
        await message.answer("❌ Пожалуйста, введи название книги")
        return

    db.add_search(user_id, query)
    await message.answer("🔍 Поиск книг...")

    books = await search_books(query)

    if not books:
        await message.answer(
            "❌ Книги не найдены. Попробуй другой запрос.",
            reply_markup=get_main_keyboard(),
        )
        return

    user_search_results[user_id] = books
    await message.answer(
        format_book_detailed(books[0], 0, len(books)),
        parse_mode="HTML",
        reply_markup=get_book_keyboards(books[0]["title"], 0, len(books)),
    )


@router.callback_query(F.data.startswith("add_library:"))
async def add_to_library_callback(callback: types.CallbackQuery):
    """Add book to library"""
    user_id = callback.from_user.id
    
    try:
        book_index = int(callback.data.split(":")[1])
        books = user_search_results.get(user_id, [])
        
        if not books or book_index >= len(books):
            await callback.answer("❌ Ошибка! Книга не найдена", show_alert=True)
            return
        
        book = books[book_index]
        
        # Check if already in library
        if db.book_in_library(user_id, book['title'], book['authors']):
            await callback.answer("⚠️ Эта книга уже в твоей библиотеке!", show_alert=True)
            return
        
        db.add_to_library(user_id, book)
        await callback.answer(f"✅ '{book['title']}' добавлена в библиотеку!")

        if book_index + 1 < len(books):
            next_book = books[book_index + 1]
            await callback.message.edit_text(
                format_book_detailed(next_book, book_index + 1, len(books)),
                parse_mode="HTML",
                reply_markup=get_book_keyboards(next_book["title"], book_index + 1, len(books)),
            )
        else:
            await callback.message.edit_text(
                "✅ Это была последняя книга из результатов поиска!\n\n"
                "Введи новый запрос для поиска"
            )
    
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("skip_book:"))
async def skip_book_callback(callback: types.CallbackQuery):
    """Legacy skip callback to show next book"""
    user_id = callback.from_user.id
    
    try:
        book_index = int(callback.data.split(":")[1])
        books = user_search_results.get(user_id, [])
        
        if not books or book_index >= len(books):
            await callback.answer("❌ Ошибка!", show_alert=True)
            return
        
        # Show next book
        if book_index + 1 < len(books):
            next_book = books[book_index + 1]
            await callback.message.edit_text(
                format_book_detailed(next_book, book_index + 1, len(books)),
                parse_mode="HTML",
                reply_markup=get_book_keyboards(next_book['title'], book_index + 1, len(books))
            )
        else:
            await callback.message.edit_text(
                "✅ Это была последняя книга!\n\n"
                "Введи новый запрос для поиска",
                reply_markup=get_main_keyboard()
            )
    
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("show_book:"))
async def show_book_callback(callback: types.CallbackQuery):
    """Show selected book by index"""
    user_id = callback.from_user.id
    
    try:
        book_index = int(callback.data.split(":")[1])
        books = user_search_results.get(user_id, [])
        
        if not books or book_index < 0 or book_index >= len(books):
            await callback.answer("❌ Ошибка! Книга не найдена", show_alert=True)
            return
        
        book = books[book_index]
        await callback.message.edit_text(
            format_book_detailed(book, book_index, len(books)),
            parse_mode="HTML",
            reply_markup=get_book_keyboards(book['title'], book_index, len(books))
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("view_library_book:"))
async def view_library_book_callback(callback: types.CallbackQuery):
    """Show a book saved in the user's library."""
    user_id = callback.from_user.id

    try:
        book_id = int(callback.data.split(":")[1])
        books = db.get_library(user_id)
        book = next((b for b in books if b["id"] == book_id), None)

        if not book:
            await callback.answer("❌ Книга не найдена!", show_alert=True)
            return

        await callback.message.edit_text(
            format_book_detailed(book, 0, 1),
            parse_mode="HTML",
            reply_markup=get_library_book_keyboard(book_id),
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data == "delete_last_book")
async def delete_last_book_callback(callback: types.CallbackQuery):
    """Delete last added book."""
    user_id = callback.from_user.id
    books = db.get_library(user_id)

    if not books:
        await callback.answer("❌ Нет книг для удаления!", show_alert=True)
        return

    last_book = books[0]
    db.remove_from_library(last_book["id"], user_id)
    await callback.answer(f"✅ '{last_book['title']}' удалена из библиотеки!")

    remaining_books = db.get_library(user_id)
    if remaining_books:
        await callback.message.edit_text(
            format_library_text(remaining_books),
            parse_mode="HTML",
            reply_markup=get_library_overview_keyboard(remaining_books),
        )
    else:
        await callback.message.edit_text("📚 Твоя библиотека пуста!")


@router.callback_query(F.data.startswith("delete_book:"))
async def delete_book_callback(callback: types.CallbackQuery):
    """Delete specific book from library."""
    user_id = callback.from_user.id

    try:
        book_id = int(callback.data.split(":")[1])
        books = db.get_library(user_id)

        book = next((b for b in books if b["id"] == book_id), None)
        if not book:
            await callback.answer("❌ Книга не найдена!", show_alert=True)
            return

        db.remove_from_library(book_id, user_id)
        await callback.answer(f"✅ '{book['title']}' удалена!")

        remaining_books = db.get_library(user_id)
        if remaining_books:
            await callback.message.edit_text(
                format_library_text(remaining_books),
                parse_mode="HTML",
                reply_markup=get_library_overview_keyboard(remaining_books),
            )
        else:
            await callback.message.edit_text("📚 Твоя библиотека пуста!")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback: types.CallbackQuery):
    """Go back to search"""
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "back_to_library")
async def back_to_library(callback: types.CallbackQuery):
    """Go back to library."""
    user_id = callback.from_user.id
    books = db.get_library(user_id)

    if not books:
        await callback.message.edit_text("📚 Твоя библиотека пуста!")
    else:
        await callback.message.edit_text(
            format_library_text(books),
            parse_mode="HTML",
            reply_markup=get_library_overview_keyboard(books),
        )
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Go back to main menu"""
    await callback.message.delete()
    await callback.answer()
