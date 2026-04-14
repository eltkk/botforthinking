import os
import aiohttp
from aiogram import Router, types, F
from aiogram.utils.chat_action import ChatActionSender
from database import add_message, get_chat_history, increment_requests

router = Router()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-exp:free"


@router.message(F.text)
async def handle_chat(message: types.Message, db_user):
    await add_message(db_user.id, "user", message.text)
    history = await get_chat_history(db_user.id)
    messages = [
        {
            "role": "system",
            "content": (
                "Ты умный и дружелюбный AI ассистент ThinkBot. "
                "Отвечай на русском языке если пользователь пишет на русском. "
                "Будь полезным, точным и кратким."
            ),
        }
    ]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            }
            payload = {"model": MODEL, "messages": messages}
            async with aiohttp.ClientSession() as session:
                async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"OpenRouter error: {resp.status} - {error_text}")
                    data = await resp.json()
                    ai_response = data["choices"][0]["message"]["content"]
            await add_message(db_user.id, "assistant", ai_response)
            await increment_requests(db_user.id)
            await message.answer(ai_response)
        except Exception as e:
            print(f"Error: {e}")
            await message.answer("⚠️ Произошла ошибка, попробуйте позже")


@router.message()
async def handle_non_text(message: types.Message):
    await message.answer("⚠️ Я принимаю только текстовые сообщения")

