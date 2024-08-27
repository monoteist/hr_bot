from datetime import datetime

from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.types import Message
from sqlalchemy.future import select

from app.utils.openai_manager import OpenaiClient
from app.database.connect import async_session
from app.database.models import User
from config import OPEN_AI_API_TOKEN



class AdaptationPlanForm(StatesGroup):
    job_title = State()
    company_name = State()
    company_activity = State()
    job_responsibilities = State()


router = Router()
openai_client = OpenaiClient(api_key=OPEN_AI_API_TOKEN)


@router.message(Command("input_employees"))
async def create_adaptation_plan_command(message: Message, state: FSMContext):
    # Проверка подписки
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(user_id=message.from_user.id))
            user = result.scalars().first()

            if user and user.subscription_end > datetime.utcnow():
                await message.answer("Я задам вам 4 вопроса, после чего пришлю готовый план адаптации.")
                await message.answer("1. Как называется должность, для которой вы составляете план адаптации?")
                await state.set_state(AdaptationPlanForm.job_title)
            else:
                await message.answer("У вас нет активной подписки. Пожалуйста, оформите подписку, чтобы использовать эту функцию.")


@router.message(StateFilter(AdaptationPlanForm.job_title))
async def answer_job_title(message: Message, state: FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer("Пожалуйста, отправьте текстовый ответ.")
        return
    await state.update_data(job_title=message.text)
    await message.answer("2. Как называется ваша компания?")
    await state.set_state(AdaptationPlanForm.company_name)


@router.message(StateFilter(AdaptationPlanForm.company_name))
async def answer_company_name(message: Message, state: FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer("Пожалуйста, отправьте текстовый ответ.")
        return
    await state.update_data(company_name=message.text)
    await message.answer("3. Чем занимается ваша компания?")
    await state.set_state(AdaptationPlanForm.company_activity)


@router.message(StateFilter(AdaptationPlanForm.company_activity))
async def answer_company_activity(message: Message, state: FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer("Пожалуйста, отправьте текстовый ответ.")
        return
    await state.update_data(company_activity=message.text)
    await message.answer("4. Какие обязанности у сотрудника на этой должности?")
    await state.set_state(AdaptationPlanForm.job_responsibilities)


@router.message(StateFilter(AdaptationPlanForm.job_responsibilities))
async def answer_job_responsibilities(message: Message, state: FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer("Пожалуйста, отправьте текстовый ответ.")
        return
    await state.update_data(job_responsibilities=message.text)
    data = await state.get_data()

    messages = [
        {"role": "system", "content": "Вы помощник по созданию планов адаптации."},
        {"role": "user", "content": f"Создайте план адаптации для следующей должности:\n\n"
                                    f"Должность: {data['job_title']}\n"
                                    f"Компания: {data['company_name']}\n"
                                    f"Вид деятельности компании: {data['company_activity']}\n"
                                    f"Обязанности на должности: {data['job_responsibilities']}"}
    ]

    response = await openai_client.async_get_response(messages)

    await message.answer(response.content)
    await state.clear()
