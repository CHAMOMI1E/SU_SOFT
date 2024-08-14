import os
import json
import logging
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.channels import (
    JoinChannelRequest,
    EditAdminRequest,
    UpdateUsernameRequest,
)
from telethon.tl.types import ChatAdminRights
from datetime import datetime
import random
import string

# Настройка логирования для вывода в консоль
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def read_session_info(session_file):
    json_file = os.path.splitext(session_file)[0] + ".json"
    with open(json_file, "r", encoding="utf-8") as file:
        session_info = json.load(file)
    return session_info


def read_2fa_password(folder):
    two_fa_file = os.path.join(folder, "twoFA.txt")
    if os.path.exists(two_fa_file):
        with open(two_fa_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None


def random_string(length=12):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


async def change_channel_link(client, channel_id):
    new_username = random_string()
    try:
        await client(UpdateUsernameRequest(channel_id, new_username))
        logging.info(f"Channel link changed to: {new_username}")
    except Exception as e:
        logging.error(f"Failed to change channel link: {e}")


async def periodic_task(session_files):
    while True:
        for session_file in session_files:
            session_info = read_session_info(session_file)
            client = TelegramClient(
                session_file, session_info["api_id"], session_info["api_hash"]
            )
            await client.start(
                phone=session_info["phone"],
                password=read_2fa_password(os.path.dirname(session_file)),
            )
            await change_channel_link(client, session_info["channel_id"])
            await client.disconnect()
        await asyncio.sleep(900)  # Sleep for 15 minutes


# Теперь интегрируем это в чат-бота на aiogram_dialog

from aiogram import Bot, Dispatcher, executor, types
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = "YOUR_BOT_TOKEN"

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Define states
from aiogram.dispatcher.filters.state import StatesGroup, State


class MyDialog(StatesGroup):
    main = State()


# Callback function for button click
async def on_click(c: types.CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Button clicked!")


# Create dialog
dialog = Dialog(
    Window(
        Const("Main Menu"),
        Row(
            Button(Const("Change Links"), id="change_links", on_click=on_click),
            Button(Const("Update List"), id="update_list", on_click=on_click),
        ),
        state=MyDialog.main,
    )
)


# Register handlers
async def start(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(MyDialog.main)


dp.register_message_handler(start, commands="start", state="*")
dialog.setup(dp)

# List of session files (update with actual paths)
session_files = ["path_to_session_file_1", "path_to_session_file_2"]

# Start polling and periodic task
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_task(session_files))
    executor.start_polling(dp, skip_updates=True)
