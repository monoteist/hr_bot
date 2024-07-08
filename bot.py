import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.database.connect import init_db
from app.handlers.handlers import router
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def on_startup():
    await init_db()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot, on_startup=on_startup)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
