import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.user_handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.include_router(router)


async def main():
    """Start the bot"""
    print("🤖 Бот запущен...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n Бот остановлен")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
