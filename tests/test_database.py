"""
Тесты для функций работы с базой данных.
Используется временная SQLite БД в памяти — не затрагивает реальные данные.
"""
import os
import pytest
import pytest_asyncio

# Переключаемся на in-memory SQLite для тестов
os.environ["DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DAILY_LIMIT"] = "5"
os.environ["ADMIN_ID"] = "999"

from database import (
    init_db,
    get_or_create_user,
    add_message,
    get_chat_history,
    increment_requests,
    clear_chat_history,
    get_stats,
    ban_user,
    unban_user,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Создаёт таблицы перед каждым тестом."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_create_user():
    """Проверяет что пользователь создаётся корректно."""
    user = await get_or_create_user(telegram_id=111, username="testuser", first_name="Test")
    assert user.telegram_id == 111
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.requests_today == 0
    assert user.is_banned is False


@pytest.mark.asyncio
async def test_get_existing_user():
    """Проверяет что повторный вызов возвращает того же пользователя."""
    user1 = await get_or_create_user(telegram_id=222, username="user2", first_name="User")
    user2 = await get_or_create_user(telegram_id=222, username="user2", first_name="User")
    assert user1.id == user2.id


@pytest.mark.asyncio
async def test_add_and_get_messages():
    """Проверяет сохранение и получение истории сообщений."""
    user = await get_or_create_user(telegram_id=333, username=None, first_name="Msg")
    await add_message(user.id, "user", "Привет!")
    await add_message(user.id, "assistant", "Здравствуй!")

    history = await get_chat_history(user.id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Привет!"
    assert history[1].role == "assistant"


@pytest.mark.asyncio
async def test_clear_chat_history():
    """Проверяет что история очищается полностью."""
    user = await get_or_create_user(telegram_id=444, username=None, first_name="Clear")
    await add_message(user.id, "user", "Сообщение 1")
    await add_message(user.id, "user", "Сообщение 2")
    await clear_chat_history(user.id)

    history = await get_chat_history(user.id)
    assert len(history) == 0


@pytest.mark.asyncio
async def test_increment_requests():
    """Проверяет что счётчик запросов увеличивается."""
    user = await get_or_create_user(telegram_id=555, username=None, first_name="Inc")
    await increment_requests(user.id)
    await increment_requests(user.id)

    updated = await get_or_create_user(telegram_id=555, username=None, first_name="Inc")
    assert updated.requests_today == 2


@pytest.mark.asyncio
async def test_ban_and_unban_user():
    """Проверяет бан и разбан пользователя."""
    user = await get_or_create_user(telegram_id=666, username="banme", first_name="Ban")
    assert user.is_banned is False

    result = await ban_user(666)
    assert result is True

    result = await unban_user(666)
    assert result is True


@pytest.mark.asyncio
async def test_ban_nonexistent_user():
    """Проверяет что бан несуществующего пользователя возвращает False."""
    result = await ban_user(99999999)
    assert result is False


@pytest.mark.asyncio
async def test_get_stats():
    """Проверяет что статистика возвращается корректно."""
    await get_or_create_user(telegram_id=777, username="stats1", first_name="S1")
    await get_or_create_user(telegram_id=888, username="stats2", first_name="S2")

    stats = await get_stats()
    assert stats["total_users"] >= 2
    assert "requests_today" in stats
    assert "total_messages" in stats
    assert "banned_users" in stats
