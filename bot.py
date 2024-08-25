import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.database.connect import init_db
from app.handlers.recruting import router as resume_router
from app.handlers.start import router as start_router
from app.handlers.subscription import router as subscription_router
from app.handlers.adaptation import router as adaptation_router
from config import TELEGRAM_BOT_TOKEN
from app.keyboards.start import get_bot_commands

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def on_startup():
    await init_db()


async def main():
    dp.include_router(resume_router)
    dp.include_router(start_router)
    dp.include_router(subscription_router)
    dp.include_router(adaptation_router)
    await bot.set_my_commands(get_bot_commands())
    await dp.start_polling(bot, on_startup=on_startup)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
