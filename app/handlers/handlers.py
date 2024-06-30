from datetime import datetime, timedelta

from aiogram import types, Router
from aiogram.filters import CommandStart
from sqlalchemy.future import select

from app.keyboards.start import start_keyboard
from app.database.connect import async_session
from app.database.models import User


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


async def test(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(select(User).filter_by(user_id=message.from_user.id))
            user = user.scalars().first()
            if user:
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            else:
                new_user = User(user_id=message.from_user.id,
                                subscription_end=datetime.utcnow() + timedelta(days=30))
                session.add(new_user)
            await session.commit()
    await message.answer("Спасибо за оплату! Ваша подписка активна на 30 дней.")
