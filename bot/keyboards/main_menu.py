from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.decorators.dec_for_kb import kb_wrap


@kb_wrap(keyboard_type='inline', adjust_keyboard=2)
def main_kb(builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
    builder.button(text='Добавить ссылку', callback_data='')
    builder.button(text='Изменить ссылку', callback_data='')
    builder.button(text='Удалить ссылку' , callback_data='')
    
    
