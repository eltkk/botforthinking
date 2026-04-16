import os
from aiogram import Router, types
from aiogram.filters import Command
from database import get_or_create_user, clear_chat_history

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}! Я ThinkBot — твой умный AI ассистент.\n\n"
        f"💬 Просто напиши мне что угодно и я отвечу.\n"
        f"⚠️ Лимит: {os.getenv('DAILY_LIMIT', '10')} запросов в день.\n\nНачнём?"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 Команды:\n/start - Начать\n/help - Помощь\n/reset - Очистить историю\n/limit - Лимит запросов"
    )


@router.message(Command("reset"))
async def cmd_reset(message: types.Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await clear_chat_history(user.id)
    await message.answer("🧹 История чата очищена!")


@router.message(Command("limit"))
async def cmd_limit(message: types.Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    limit = int(os.getenv("DAILY_LIMIT", 10))
    left = max(0, limit - user.requests_today)
    await message.answer(f"📊 Осталось запросов: {left} из {limit} на сегодня.")

