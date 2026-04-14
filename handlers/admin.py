import os
import asyncio
from aiogram import Router, Bot, types
from aiogram.filters import Command
from database import get_stats, ban_user, unban_user, get_all_users

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        return False
    return user_id == int(admin_id)


@router.message(Command("stats"))
async def cmd_stats(message: types.Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    stats = await get_stats()
    await message.answer(
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: <b>{stats['total_users']}</b>\n"
        f"💬 Запросов сегодня: <b>{stats['requests_today']}</b>\n"
        f"📨 Сообщений всего: <b>{stats['total_messages']}</b>\n"
        f"🚫 Заблокировано: <b>{stats['banned_users']}</b>",
        parse_mode="HTML",
    )


@router.message(Command("ban"))
async def cmd_ban(message: types.Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ Использование: /ban <telegram_id>\nПример: /ban 123456789")
        return
    target_id = int(parts[1])
    success = await ban_user(target_id)
    if success:
        await message.answer(f"🚫 Пользователь <code>{target_id}</code> заблокирован.", parse_mode="HTML")
    else:
        await message.answer(f"❌ Пользователь с ID <code>{target_id}</code> не найден.", parse_mode="HTML")


@router.message(Command("unban"))
async def cmd_unban(message: types.Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ Использование: /unban <telegram_id>\nПример: /unban 123456789")
        return
    target_id = int(parts[1])
    success = await unban_user(target_id)
    if success:
        await message.answer(f"✅ Пользователь <code>{target_id}</code> разблокирован.", parse_mode="HTML")
    else:
        await message.answer(f"❌ Пользователь с ID <code>{target_id}</code> не найден.", parse_mode="HTML")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, bot: Bot) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("⚠️ Использование: /broadcast <текст сообщения>")
        return
    text = parts[1].strip()
    users = await get_all_users()
    sent = 0
    failed = 0
    for user in users:
        try:
            await bot.send_message(user.telegram_id, f"📢 <b>Сообщение от администратора:</b>\n\n{text}", parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)  # Небольшая пауза чтобы не превысить лимит Telegram
        except Exception:
            failed += 1
    await message.answer(
        f"✅ Рассылка завершена.\n"
        f"📤 Отправлено: <b>{sent}</b>\n"
        f"❌ Не доставлено: <b>{failed}</b>",
        parse_mode="HTML",
    )
