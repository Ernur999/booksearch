from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_book_keyboards(book_title: str, book_index: int, total_books: int) -> InlineKeyboardMarkup:
    """Get keyboard for book actions"""
    buttons = [
        [
            InlineKeyboardButton(text="📚 Добавить в библиотеку", callback_data=f"add_library:{book_index}"),
        ]
    ]

    nav_buttons = []
    if book_index > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"show_book:{book_index - 1}")
        )
    if book_index + 1 < total_books:
        nav_buttons.append(
            InlineKeyboardButton(text="Вперед ▶️", callback_data=f"show_book:{book_index + 1}")
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main keyboard with buttons"""
    buttons = [
        [KeyboardButton(text="📚 Моя библиотека")],
        [KeyboardButton(text="🔍 История поисков"), KeyboardButton(text="❌ История последних")],
        [KeyboardButton(text="ℹ️ Справка")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_library_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for library management"""
    buttons = [
        [InlineKeyboardButton(text="🗑️ Удалить последнюю", callback_data="delete_last_book")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_library_book_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for individual library book"""
    buttons = [
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_book:{book_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_library")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_history_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for search history"""
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
