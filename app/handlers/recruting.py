from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter
from sqlalchemy.future import select

from app.database.connect import async_session
from app.database.models import User
from app.utils.openai_manager import OpenaiClient
from config import OPEN_AI_API_TOKEN

router = Router()
openai_client = OpenaiClient(api_key=OPEN_AI_API_TOKEN)

# Определение состояний для создания резюме


class VacancyForm(StatesGroup):
    company_name = State()
    company_activity = State()
    job_title = State()
    job_responsibilities = State()

class EditVacancyForm(StatesGroup):
    vacancy_text = State()

class InterviewQuestionsForm(StatesGroup):
    job_title = State()
    company_activity = State()
    required_skills = State()
    candidate_experience = State()


def text_message_filter(message: types.Message) -> bool:
    return message.content_type == 'text'


@router.message(Command("recruiting"))
async def recruiting_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать вакансию", callback_data="create_vacancy")],
        [InlineKeyboardButton(text="Редактировать вакансию", callback_data="edit_vacancy")],
        [InlineKeyboardButton(text="Подготовить вопросы к собеседованию", callback_data="prepare_interview_questions")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)




@router.message(StateFilter(ResumeForm.name), text_message_filter)
async def answer_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer("2. Какую должность вы хотите получить?")
    await state.set_state(ResumeForm.position)


@router.message(StateFilter(ResumeForm.position), text_message_filter)
async def answer_position(message: types.Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await message.answer("3. Какой у вас опыт работы?")
    await state.set_state(ResumeForm.experience)


@router.message(StateFilter(ResumeForm.experience), text_message_filter)
async def answer_experience(message: types.Message, state: FSMContext) -> None:
    await state.update_data(experience=message.text)
    await message.answer("4. Какие у вас навыки?")
    await state.set_state(ResumeForm.skills)


@router.message(StateFilter(ResumeForm.skills), text_message_filter)
async def answer_skills(message: types.Message, state: FSMContext) -> None:
    await state.update_data(skills=message.text)
    await message.answer("5. Напишите кратко о себе.")
    await state.set_state(ResumeForm.summary)


@router.message(StateFilter(ResumeForm.summary), text_message_filter)
async def answer_summary(message: types.Message, state: FSMContext) -> None:
    await state.update_data(summary=message.text)
    data = await state.get_data()

    messages = [
        {"role": "system", "content": "You are a resume writing assistant."},
        {"role": "user", "content": f"Create a resume for the following information:\n\n"
                                    f"Name: {data['name']}\n"
                                    f"Position: {data['position']}\n"
                                    f"Experience: {data['experience']}\n"
                                    f"Skills: {data['skills']}\n"
                                    f"Summary: {data['summary']}"}
    ]

    response = await openai_client.async_get_response(messages)
    await message.answer(response['content'])
    await state.clear()


@router.message(Command("create_vacancy"))
async def create_vacancy_command(message: types.Message, state: FSMContext) -> None:
    """
    Команда для создания вакансии. Проверяет наличие активной подписки и начинает процесс, если подписка активна.
    """
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(user_id=message.from_user.id))
            user = result.scalars().first()
            if user and user.subscription_end > datetime.utcnow():
                await message.answer("Отлично! Я задам вам 4 вопроса, после чего пришлю готовую вакансию.")
                await message.answer("1. Как называется ваша компания?")
                await state.set_state(VacancyForm.company_name)
            else:
                await message.answer("У вас нет активной подписки. Пожалуйста, оформите подписку, чтобы использовать эту функцию.")


@router.message(StateFilter(VacancyForm.company_name), text_message_filter)
async def answer_company_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(company_name=message.text)
    await message.answer("2. Чем занимается ваша компания?")
    await state.set_state(VacancyForm.company_activity)


@router.message(StateFilter(VacancyForm.company_activity), text_message_filter)
async def answer_company_activity(message: types.Message, state: FSMContext) -> None:
    await state.update_data(company_activity=message.text)
    await message.answer("3. Как называется должность, которую вы ищете?")
    await state.set_state(VacancyForm.job_position)


@router.message(StateFilter(VacancyForm.job_position), text_message_filter)
async def answer_job_position(message: types.Message, state: FSMContext) -> None:
    await state.update_data(job_position=message.text)
    await message.answer("4. Опишите ключевой функционал на этой должности.")
    await state.set_state(VacancyForm.job_functionality)


@router.message(StateFilter(VacancyForm.job_functionality), text_message_filter)
async def answer_job_functionality(message: types.Message, state: FSMContext) -> None:
    await state.update_data(job_functionality=message.text)
    data = await state.get_data()

    messages = [
        {"role": "system", "content": "You are a job vacancy creation assistant."},
        {"role": "user", "content": f"Create a job vacancy for the following information:\n\n"
                                    f"Company Name: {data['company_name']}\n"
                                    f"Company Activity: {data['company_activity']}\n"
                                    f"Position: {data['job_position']}\n"
                                    f"Functionality: {data['job_functionality']}"}
    ]

    response = await openai_client.async_get_response(messages)
    await message.answer(response.choices[0].message.content)
    await state.clear()
