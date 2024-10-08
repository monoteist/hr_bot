from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand


def start_keyboard():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Опробовать бесплатно 24 часа",
                    callback_data="start_trial",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Купить подписку",
                    callback_data="buy_subscription"
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


def get_bot_commands():
    """
    Возвращает список команд для меню бота.
    """
    commands = [
        BotCommand(command="/adaptation_plan", description="Создать план адаптации"),
        BotCommand(command="/recruiting", description="Рекрутинг"),
        BotCommand(command="/your_assistant", description="Твой помощник"),
    ]
    return commands