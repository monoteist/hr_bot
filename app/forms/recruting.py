from aiogram.fsm.state import StatesGroup, State


class VacancyForm(StatesGroup):
    company_name = State()
    company_activity = State()
    job_title = State()
    job_functionality = State()
    editing_vacancy = State()


class InterviewQuestionForm(StatesGroup):
    job_title = State()
    company_activity = State()
    required_skills = State()
    candidate_experience = State()