import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram_dialog.setup import DialogRegistry, setup_dialogs

from bot.windows.main.menu import MainMenuWin
from aiogram_dialog import LaunchMode, Dialog

from bot.windows.main.views import start
from config.settings import BOT_KEY
from aiogram.filters import CommandStart, Command

bot = Bot(BOT_KEY)
dp = Dispatcher()

DLGS = (Dialog(*MainMenuWin, launch_mode=LaunchMode.ROOT),)


async def background_task():
    while True:
        print("Фоновая задача выполняется каждые 15 минут.")
        await asyncio.sleep(7)


def register_dialogs(dp):
    for DLG in DLGS:
        dp.include_router(DLG)


async def start_bot() -> None:
    register_dialogs(dp)
    setup_dialogs(dp)
    dp.message.register(start, Command('start'))

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
