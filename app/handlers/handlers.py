from datetime import datetime, timedelta

from aiogram import types, Router, F
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


@router.callback_query(F.data == 'start_trial')
async def start_trial(callback_query: types.CallbackQuery):
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(select(User).filter_by(user_id=callback_query.from_user.id))
            user = user.scalars().first()
            if user:
                if user.has_used_trial:
                    await callback_query.message.answer("Вы уже использовали пробный период.")
                    return
                else:
                    user.subscription_end = datetime.utcnow() + timedelta(days=1)
                    user.has_used_trial = True
            else:
                new_user = User(
                    user_id=callback_query.from_user.id,
                    subscription_end=datetime.utcnow() + timedelta(days=1),
                    has_used_trial=True
                )
                session.add(new_user)
            await session.commit()

    await callback_query.message.answer(
        "Вы начали бесплатный пробный период 24 часа. После окончания пробного периода мы напомним вам о подписке.\n\n"
        "Все функции доступны в меню бота.\n\n"
        "Удачного и эффективного использования нашего бота!"
    )
    await callback_query.answer()


# async def test(message: types.Message):
#     async with async_session() as session:
#         async with session.begin():
#             user = await session.execute(select(User).filter_by(user_id=message.from_user.id))
#             user = user.scalars().first()
#             if user:
#                 user.subscription_end = datetime.utcnow() + timedelta(days=30)
#             else:
#                 new_user = User(user_id=message.from_user.id,
#                                 subscription_end=datetime.utcnow() + timedelta(days=30))
#                 session.add(new_user)
#             await session.commit()
#     await message.answer("Спасибо за оплату! Ваша подписка активна на 30 дней.")
