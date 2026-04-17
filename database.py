import os
from datetime import datetime, date
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, User, Message

load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///data/thinkbot.db")
engine = create_async_engine(DB_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create_user(
    telegram_id: int, username: Optional[str], first_name: Optional[str]
) -> User:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


async def add_message(user_id: int, role: str, content: str) -> None:
    async with AsyncSessionLocal() as session:
        message = Message(user_id=user_id, role=role, content=content)
        session.add(message)
        await session.commit()


async def get_chat_history(user_id: int, limit: int = 20) -> list[Message]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(messages[::-1])


async def reset_daily_limit_if_needed(user: User) -> User:
    today = datetime.utcnow().date()
    if user.last_reset_date != today:
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(requests_today=0, last_reset_date=today)
            )
            await session.commit()
            user.requests_today = 0
            user.last_reset_date = today
    return user


async def increment_requests(user_id: int) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(requests_today=User.requests_today + 1)
        )
        await session.commit()


async def clear_chat_history(user_id: int) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Message).where(Message.user_id == user_id))
        await session.commit()


# --- Admin функции ---

async def get_stats() -> dict:
    """Возвращает общую статистику бота."""
    async with AsyncSessionLocal() as session:
        total_users = await session.scalar(select(func.count(User.id)))
        today = datetime.utcnow().date()
        requests_today = await session.scalar(
            select(func.sum(User.requests_today)).where(User.last_reset_date == today)
        )
        total_messages = await session.scalar(select(func.count(Message.id)))
        banned_users = await session.scalar(
            select(func.count(User.id)).where(User.is_banned.is_(True))
        )
        return {
            "total_users": total_users or 0,
            "requests_today": requests_today or 0,
            "total_messages": total_messages or 0,
            "banned_users": banned_users or 0,
        }


async def ban_user(telegram_id: int) -> bool:
    """Банит пользователя. Возвращает True если пользователь найден."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_banned=True)
        )
        await session.commit()
        return True


async def unban_user(telegram_id: int) -> bool:
    """Разбанивает пользователя. Возвращает True если пользователь найден."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_banned=False)
        )
        await session.commit()
        return True


async def get_all_users() -> list[User]:
    """Возвращает всех незабаненных пользователей (для broadcast)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.is_banned.is_(False))
        )
        return list(result.scalars().all())
