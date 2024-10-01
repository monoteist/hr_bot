from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import User
from app.database.connect import async_session


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
    Обновляет или добавляет подписку пользователю, суммируя оставшиеся дни,
    если подписка еще активна.

    :param session: Сессия базы данных.
    :param user_id: ID пользователя в Telegram.
    :param days: Количество дней, на которое продлевается подписка.
    """
    user = await get_user(session, user_id)
    current_date = datetime.utcnow()

    if user:
        if user.subscription_end and user.subscription_end > current_date:
            # Если у пользователя активная подписка, суммируем оставшиеся дни
            remaining_days = (user.subscription_end - current_date).days
            user.subscription_end = current_date + \
                timedelta(days=days + remaining_days)
        else:
            # Если подписки нет или она истекла, устанавливаем новые дни
            user.subscription_end = current_date + timedelta(days=days)
    else:
        # Если пользователь новый, создаем его с новой подпиской
        new_user = User(
            user_id=user_id,
            subscription_end=current_date + timedelta(days=days)
        )
        session.add(new_user)

    await session.commit()


async def check_subscription(user_id: int) -> User:
    """
    Проверяет наличие активной подписки у пользователя, открывая сессию базы данных.

    :param user_id: ID пользователя Telegram.
    :return: Объект пользователя с активной подпиской или None, если подписка отсутствует.
    """
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(user_id=user_id))
            user = result.scalars().first()

            if user and user.subscription_end > datetime.utcnow():
                return user
