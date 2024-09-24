from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_subscription_keyboard():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="На 1 месяц: 4 990 рублей",
                    callback_data="subscribe_1_month"
                )
            ],
            [
                InlineKeyboardButton(
                    text="На 3 месяца: 11 990 рублей",
                    callback_data="subscribe_3_months"
                )
            ],
            [
                InlineKeyboardButton(
                    text="На год: 39 990 рублей",
                    callback_data="subscribe_1_year"
                )
            ]
        ]
    )
    return markup
