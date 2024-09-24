from datetime import datetime, timedelta

from aiogram import types, Router, F

from app.database.connect import async_session
from app.database.models import User
from app.utils.db import get_user, update_subscription
from config import YOOKASSA_TEST_TOKEN
from app.keyboards.subscription import get_subscription_keyboard

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
                    await callback_query.answer()
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
async def buy_subscription(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "Вы можете приобрести подписку в трех вариантах:\n"
        "1. На 1 месяц: 4 990 рублей\n"
        "2. На 3 месяца: 11 990 рублей\n"
        "3. На год: 39 990 рублей\n"
        "Выберите подходящий вариант:",
        reply_markup=get_subscription_keyboard()
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith('subscribe_'))
async def process_callback_buy_subscribe(callback_query: types.CallbackQuery):
    """
    Обработчик для покупки подписки. Отправляет пользователю счет на оплату.

    :param callback_query: Callback query от пользователя.
    """
    data = callback_query.data
    if data == "subscribe_1_month":
        prices = [types.LabeledPrice(label="Месячная подписка", amount=800 * 100)]
    elif data == "subscribe_3_months":
        prices = [types.LabeledPrice(label="Подписка на 3 месяца", amount=900 * 100)]
    elif data == "subscribe_1_year":
        prices = [types.LabeledPrice(label="Годовая подписка", amount=990 * 100)]
    else:
        await callback_query.answer("Некорректный выбор.")
        return

    await callback_query.message.answer_invoice(
        title="Подписка",
        description="Оплатите выбранную подписку",
        payload=f"subscription_payload_{data}",
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
            payload = message.successful_payment.invoice_payload
            if payload == "subscription_payload_subscribe_1_month":
                days = 30
            elif payload == "subscription_payload_subscribe_3_months":
                days = 90
            elif payload == "subscription_payload_subscribe_1_year":
                days = 365
            else:
                await message.answer("Ошибка при обработке платежа.")
                return
            await update_subscription(session, message.from_user.id, days)
    await message.answer(
        f"Поздравляем с приобретением подписки!\n"
        f"Весь функционал вы можете найти в меню бота.\n"
        f"Удачного и эффективного использования нашего бота!"
    )
