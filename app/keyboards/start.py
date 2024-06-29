from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Опробовать беспалтно 24 часа",
                    callback_data='some_text',
                )
            ],
            [
                InlineKeyboardButton(
                    text="Купить подписку",
                    callback_data='some_text',
                )
            ],
            [
                InlineKeyboardButton(
                    text="Задать вопрос",
                    callback_data='some_text',
                )
            ],
        ]
    )
    return markup
