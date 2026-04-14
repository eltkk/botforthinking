import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database import init_db
from handlers import start, chat, admin
from middlewares.limit import LimitMiddleware

load_dotenv()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    await init_db()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.message.middleware(LimitMiddleware())
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(chat.router)
    logging.info("ThinkBot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
