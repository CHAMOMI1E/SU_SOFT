import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot.routers.add import add_router
from bot.routers.delete import delete_router
from bot.routers.edit import edit_router
from bot.routers.start import main_router
from config.settings import BOT_KEY

bot = Bot(BOT_KEY, parse_mode=ParseMode.HTML)
dp = Dispatcher()


async def background_task():
    while True:
        print("Фоновая задача выполняется каждые 15 минут.")
        await asyncio.sleep(7)


async def start_bot() -> None:
    dp.include_routers(main_router, add_router, edit_router, delete_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s"
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        stream=sys.stdout,
    )

    try:
        current_script_path = os.path.abspath(__file__)
        project_root = os.path.dirname(current_script_path)
        session_path = os.path.join(project_root, "soft", "session")
        print(session_path)
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Shutting down")
