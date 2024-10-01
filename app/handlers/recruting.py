from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter

from app.utils.openai_manager import OpenaiClient
from app.keyboards.recruting import get_recruiting_menu
from app.utils.validators import text_message_filter
from app.utils.db import check_subscription


from config import OPEN_AI_API_TOKEN

router = Router()
openai_client = OpenaiClient(api_key=OPEN_AI_API_TOKEN)


class VacancyForm(StatesGroup):
    company_name = State()
    company_activity = State()
    job_title = State()
    job_functionality = State()


@router.message(Command("recruiting"))
async def recruiting_menu(message: types.Message):
    keyboard = get_recruiting_menu()
    await message.answer("Выберите действие:", reply_markup=keyboard)


@router.callback_query(F.data == 'create_vacancy')
async def create_vacancy_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user = await check_subscription(callback_query.from_user.id)
    if user:
        await callback_query.message.answer("Я задам вам 4 вопроса, после чего пришлю готовую вакансию.")
        await callback_query.message.answer("1. Как называется ваша компания?")
        await state.set_state(VacancyForm.company_name)
    else:
        await callback_query.message.answer("У вас нет активной подписки. Пожалуйста, оформите подписку, чтобы использовать эту функцию.")


@router.message(StateFilter(VacancyForm.company_name), text_message_filter)
async def answer_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer("2. Чем занимается ваша компания?")
    await state.set_state(VacancyForm.company_activity)


@router.message(StateFilter(VacancyForm.company_activity), text_message_filter)
async def answer_company_activity(message: types.Message, state: FSMContext):
    await state.update_data(company_activity=message.text)
    await message.answer("3. Как называется должность, которую вы ищете?")
    await state.set_state(VacancyForm.job_title)


@router.message(StateFilter(VacancyForm.job_title), text_message_filter)
async def answer_job_title(message: types.Message, state: FSMContext):
    await state.update_data(job_title=message.text)
    await message.answer("4. Опишите ключевой функционал на этой должности.")
    await state.set_state(VacancyForm.job_functionality)


@router.message(StateFilter(VacancyForm.job_functionality), text_message_filter)
async def answer_job_functionality(message: types.Message, state: FSMContext):
    await state.update_data(job_functionality=message.text)
    data = await state.get_data()

    messages = [
        {"role": "system", "content": "Вы помощник по созданию вакансий."},
        {"role": "user", "content": f"Создайте описание вакансии для следующей информации:\n\n"
         f"Компания: {data['company_name']}\n"
         f"Вид деятельности компании: {data['company_activity']}\n"
         f"Должность: {data['job_title']}\n"
         f"Ключевой функционал: {data['job_functionality']}"}
    ]

    response = await openai_client.async_get_response(messages)

    await message.answer(response.content)
    await state.clear()


@router.message(StateFilter(VacancyForm))
async def handle_non_text_message(message: types.Message) -> None:
    await message.answer("Пожалуйста, отправьте текстовое сообщение.")
