import logging

from aiogram import types
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.states.main import MainSG


async def add_link(message: types.Message, dialog: DialogManager):
    link = message.text
    await message.answer(text=f"Ссылка добавлена: {link}")
    await dialog.switch_to(MainSG.start)


async def start(message: types.Message, dialog_manager: DialogManager | None = None):
    user_id = message.chat.id
    logging.warning(f"Бот был запущен пользователем {message.from_user.username}")
    await dialog_manager.start(state=MainSG.start, mode=StartMode.RESET_STACK)
