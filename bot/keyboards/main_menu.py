from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram_widgets.pagination import KeyboardPaginator

from bot.decorators.dec_for_kb import kb_wrap


@kb_wrap(keyboard_type='inline', adjust_keyboard=2)
def main_kb(builder: InlineKeyboardBuilder):
    builder.button(text='Добавить ссылку', callback_data='func_add_url')


def list_of_url(urls: Dict):
    buttons = [
        InlineKeyboardButton(text=f'{url}', callback_data=f'add_{id_url}')
        for id_url, url in urls.items()
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        per_page=20,
        per_row=2,
    )
    return paginator.as_markup()
