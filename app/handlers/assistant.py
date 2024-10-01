from aiogram import Router, types, F
from aiogram.filters import Command


from app.utils.openai_manager import OpenaiClient
from config import OPEN_AI_API_TOKEN

router = Router()
openai_client = OpenaiClient(api_key=OPEN_AI_API_TOKEN)


@router.message(Command("your_assistant"))
async def your_assistant_command(message: types.Message):
    """
    Обработчик команды /your_assistant.
    Отправляет приветственное сообщение от виртуального HR-ассистента.
    """
    welcome_message = (
        "Привет! Я твой виртуальный HR-ассистент.\n"
        "Ты можешь задать мне любой вопрос по управлению персоналом.\n"
        "Буду рад помочь!"
    )
    await message.answer(welcome_message)

    await message.answer("Вы можете начать задавать свои вопросы прямо сейчас.")


@router.message(F.text)
async def handle_user_message(message: types.Message):
    """
    Обработчик всех текстовых сообщений.
    Если пользователь не отправляет команду, передаем вопрос в OpenAI и отправляем ответ.
    """
    if message.text.startswith('/'):
        return

    user_message = message.text
    messages = [
        {"role": "system", "content": "Вы HR-ассистент."},
        {"role": "user", "content": user_message}
    ]

    response = await openai_client.async_get_response(messages)

    await message.answer(response.content)
