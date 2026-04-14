import os
from typing import Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from database import get_or_create_user, reset_daily_limit_if_needed


class LimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        # Команды не считаются в лимит — пропускаем проверку
        if not event.text or event.text.startswith("/"):
            return await handler(event, data)

        user_tg = event.from_user
        user = await get_or_create_user(user_tg.id, user_tg.username, user_tg.first_name)

        # Проверяем бан
        if user.is_banned:
            await event.answer("🚫 Вы заблокированы и не можете использовать бота.")
            return

        user = await reset_daily_limit_if_needed(user)
        limit = int(os.getenv("DAILY_LIMIT", 10))

        if user.requests_today >= limit:
            await event.answer(f"❌ Лимит {limit} запросов в день исчерпан. Возвращайтесь завтра!")
            return

        data["db_user"] = user
        return await handler(event, data)
