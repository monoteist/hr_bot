from aiogram.fsm.state import StatesGroup, State


class AdaptationPlanForm(StatesGroup):
    job_title = State()
    company_name = State()
    company_activity = State()
    job_responsibilities = State()
