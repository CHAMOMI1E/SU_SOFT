import logging

from aiogram import types
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.states.main import MainSG
from db.requests.link import get_all_links


async def add_link(message: types.Message, __, dialog: DialogManager):
    link = message.text
    await message.answer(f"Ссылка добавлена: {link}")
    await dialog.switch_to(MainSG.start)


async def show_links(c: CallbackQuery, __, dialog: DialogManager):
    lst = await get_all_links()
    lst = lst[0]
    await c.message.answer(f"{lst.url}")
    await dialog.switch_to(MainSG.start)


async def start(message: types.Message, dialog_manager: DialogManager | None = None):
    logging.warning(f"Бот был запущен пользователем {message.from_user.username}")
    await dialog_manager.start(state=MainSG.start, mode=StartMode.RESET_STACK)
