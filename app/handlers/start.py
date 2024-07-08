from aiogram import types, Router
from aiogram.filters import CommandStart

from app.keyboards.start import start_keyboard


router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    start_text = (
        f"Этот бот поможет вам решить любой вопрос по управлению персоналом."
        f"Здесь возможность создания вакансии, матрица подбора, шаблоны документов, "
        f"виртуальный ассистент и многое другое."
        f"До приобретения подписки вы можете опробовать этот бот бесплатно."
        f"Создатель бота: @мойтелеграмканал"
    )
    await message.answer(
        start_text, reply_markup=start_keyboard()
    )
