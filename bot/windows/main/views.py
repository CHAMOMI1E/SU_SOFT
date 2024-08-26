import asyncio
import logging

from aiogram import types
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from bot.states.main import MainSG
from db.requests.link import add_url, delete_link, get_all_links, update_link


async def add_link(message: types.Message, __, dialog: DialogManager):
    link = message.text
    await add_url(link)
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


def get_link_buttons(**kwargs):
    links = asyncio.run(get_all_links())
    buttons = [
        Button(Const(link.url), id=f"link_{link.id}", on_click=on_link_button_click)
        for link in links
    ]
    return buttons


async def on_link_button_click(c: CallbackQuery, button: Button, manager: DialogManager, link_id: str):
    # Обработка нажатия на кнопку
    await c.message.answer(f"Вы нажали на ссылку с ID: {link_id}")
    await manager.switch_to(MainSG.start)
    # Здесь можно добавить логику для изменения или удаления ссылки


async def edit_link(callback_query, dialog_manager):
    link_id = dialog_manager.current_context().dialog_data.get("link_id")
    new_url = dialog_manager.current_context().dialog_data.get("new_url")
    if link_id and new_url:
        await update_link(link_id, new_url)
        await callback_query.message.answer("Ссылка успешно изменена.")
    else:
        await callback_query.message.answer("Не удалось изменить ссылку. Проверьте ввод.")

async def confirm_delete_link(callback_query, dialog_manager):
    link_id = dialog_manager.current_context().dialog_data.get("link_id")
    if link_id:
        await delete_link(link_id)
        await callback_query.message.answer("Ссылка успешно удалена.")
    else:
        await callback_query.message.answer("Не удалось удалить ссылку. Проверьте ввод.")
        
        
async def receive_new_url(message: types.Message, dialog_manager: DialogManager):
    link_id = dialog_manager.dialog_data.get('link_id')
    new_url = message.text
    await update_link(link_id, new_url)  # Обновляем URL в базе данных
    await message.answer(f"Ссылка обновлена: {new_url}")
    await dialog_manager.switch_to(MainSG.start)