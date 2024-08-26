from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, SwitchTo, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from bot.states.main import MainSG
from bot.windows.main.views import add_link, confirm_delete_link, edit_link, get_link_buttons, receive_new_url, show_links

MainMenuWin = [
    Window(
        Const(
            "Доброго времени суток. С вами на связи *SLBot*\n"
            "Высылаю вам клавиатуру для взаимодействия с нашим софтом"
        ),
        SwitchTo(Const("Добавить ссылку"), id="add_link", state=MainSG.add_link),
        SwitchTo(Const("Изменить ссылку"), id="edit_link", state=MainSG.edit_link),
        Button(Const("Удалить ссылку"), id="delete_link", on_click=confirm_delete_link),
        parse_mode="markdown",
        state=MainSG.start,
    ),
    Window(
        Const("Введите ссылку"),
        MessageInput(func=add_link),
        SwitchTo(Const("Назад"), id="main", state=MainSG.start),
        parse_mode="markdown",
        state=MainSG.add_link,
    ),
    Window(
        Const("Введите ID ссылки для удаления"),
        MessageInput(func=confirm_delete_link),
        SwitchTo(Const("Назад"), id="main", state=MainSG.start),
        parse_mode="markdown",
        state=MainSG.delete_link,
    ),
    Window(
        Const("Выберите ссылку для изменения"),
        ScrollingGroup(
            *get_link_buttons(),
            id="links_pagination",
            height=5,
            width=2,
            hide_on_single_page=True,
        ),
        SwitchTo(Const("Назад"), id="main", state=MainSG.start),
        parse_mode="markdown",
        state=MainSG.edit_link,
    ),
    Window(
        Const("Введите новый URL для ссылки"),
        MessageInput(func=receive_new_url),
        SwitchTo(Const("Назад"), id="main", state=MainSG.start),
        parse_mode="markdown",
        state=MainSG.receive_new_url,
    ),
]
