from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import User


async def get_user(session: AsyncSession, user_id: int) -> User:
    """
    Получает пользователя из базы данных по его ID.

    :param session: Сессия базы данных.
    :param user_id: ID пользователя в Telegram.
    :return: Объект User, если найден, иначе None.
    """
    user = await session.execute(select(User).filter_by(
        user_id=user_id
    ))
    return user.scalars().first()


async def update_subscription(session: AsyncSession, user_id: int, days: int):
    """
    Обновляет или создает дату окончания подписки пользователя.

    :param session: Сессия базы данных.
    :param user_id: ID пользователя в Telegram.
    :param days: Количество дней, на которое продлевается подписка.
    """
    user = await get_user(session, user_id)
    if user:
        user.subscription_end = datetime.utcnow() + timedelta(days=days)
    else:
        new_user = User(
            user_id=user_id,
            subscription_end=datetime.utcnow() + timedelta(days=days)
        )
        session.add(new_user)
    await session.commit()
