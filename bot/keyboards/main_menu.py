from typing import List, Dict

from aiogram import Router
from aiogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram_widgets.pagination import KeyboardPaginator

from bot.decorators.dec_for_kb import kb_wrap


@kb_wrap(keyboard_type="inline", adjust_keyboard=1)
def main_kb(builder: InlineKeyboardBuilder):
    builder.button(text="Добавить ссылку", callback_data="func_add_url")
    builder.button(text="Изменить ссылку", callback_data="func_edit_url")
    builder.button(text="Удалить ссылку", callback_data="func_del_url")


def list_of_urls(urls: Dict, router: Router, action: str):
    buttons = [
        InlineKeyboardButton(text=f"{url.url}", callback_data=f"{action}_{url.id}")
        for url in urls
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        additional_buttons=[[InlineKeyboardButton(text="Назад", callback_data="home")]],
        per_page=20,
        per_row=2,
        router=router,
    )

    return paginator.as_markup()


@kb_wrap(keyboard_type="inline", adjust_keyboard=2)
def page_of_urls(builder: InlineKeyboardBuilder, urls: Dict, action: str):
    for url in urls:
        builder.button(text=f"{url.url}", callback_data=f"{action}_{url.id}")
    builder.button(text="Назад", callback_data="home")


@kb_wrap(keyboard_type="inline", adjust_keyboard=2)
def del_url_kb(builder: InlineKeyboardBuilder, url_id: int):
    builder.button(text="Отмена", callback_data="home")
    builder.button(text="Удалить", callback_data=f"del-url_{url_id}")



@kb_wrap(keyboard_type="inline", adjust_keyboard=1)
def back_kb(builder: InlineKeyboardBuilder):
    builder.button(text="Отмена", callback_data="home")
