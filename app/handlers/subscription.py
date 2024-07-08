from datetime import datetime, timedelta

from aiogram import types, Router, F

from app.database.connect import async_session
from app.database.models import User
from app.utils.db import get_user, update_subscription
from config import YOOKASSA_TEST_TOKEN

router = Router()


@router.callback_query(F.data == 'start_trial')
async def start_trial(callback_query: types.CallbackQuery):
    """
    Обработчик для начала бесплатного пробного периода.
    Предоставляет пользователю один день пробного периода, если он еще не использовал его.

    :param callback_query: Callback query от пользователя.
    """
    async with async_session() as session:
        async with session.begin():
            user_id = callback_query.from_user.id
            user = await get_user(session=session, user_id=user_id)
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
    """
    Обработчик для покупки подписки. Отправляет пользователю счет на оплату.

    :param callback_query: Callback query от пользователя.
    """
    # Цена в копейках (490 рублей)
    prices = [types.LabeledPrice(label="Месячная подписка", amount=490 * 100)]
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
    """
    Обработчик предчекового запроса. Подтверждает, что оплата может быть проведена.

    :param pre_checkout_query: Предчековый запрос от пользователя.
    """
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: types.Message):
    """
    Обработчик успешной оплаты. Обновляет дату окончания подписки пользователя.

    :param message: Сообщение, содержащее информацию об успешной оплате.
    """
    async with async_session() as session:
        async with session.begin():
            await update_subscription(session, message.from_user.id, 30)
    await message.answer(
        f"Поздравляем с приобретением подписки!\n"
        f"Весь функционал вы можете найти в меню бота.\n"
        f"Удачного и эффективного использования нашего бота!"
    )
