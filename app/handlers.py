from aiogram import types, Router
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Это hr бот.")