from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_recruiting_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать вакансию",
                              callback_data="create_vacancy")],
        [InlineKeyboardButton(text="Редактировать вакансию",
                              callback_data="edit_vacancy")],
        [InlineKeyboardButton(text="Подготовить вопросы к собеседованию",
                              callback_data="prepare_interview_questions")]
    ])
    return keyboard
