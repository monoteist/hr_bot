from datetime import datetime, timedelta

from aiogram import types, Router, F
from aiogram.filters import CommandStart
from sqlalchemy.future import select

from app.keyboards.start import start_keyboard
from app.database.connect import async_session
from app.database.models import User
from config import YOOKASSA_TEST_TOKEN


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


@router.callback_query(F.data == 'buy_subscription')
async def process_callback_buy_subscribe(callback_query: types.CallbackQuery):
    # Цена в копейках (490 рублей)
    prices = [types.LabeledPrice(label="Месячная подписка", amount=49000)]
    await callback_query.message.answer_invoice(
        title="Подписка на месяц",
        description="Оплатите месячную подписку",
        payload="subscription_payload",
        provider_token=YOOKASSA_TEST_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="subscription"
    )
    await callback_query.answer()


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query_handler(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(select(User).filter_by(user_id=message.from_user.id))
            user = user.scalars().first()
            if user:
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            else:
                new_user = User(
                    user_id=message.from_user.id,
                    subscription_end=datetime.utcnow() + timedelta(days=30)
                )
                session.add(new_user)
            await session.commit()
    await message.answer(
        f"Поздравляем с приобретением подписки!\n"
        f"Весь функционал вы можете найти в меню бота.\n"
        f"Удачного и эффективного использования нашего бота!»"
    )


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
