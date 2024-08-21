from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, SwitchTo, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from bot.states.main import MainSG
from bot.windows.main.views import add_link, show_links

MainMenuWin = [
    Window(
        Const(
            """
        Доброго времени суток. С вами на связи *SLBot*\n
        Высылаю вам клавиатуру для взаимодействия с нашим софтом
        """
        ),
        SwitchTo(Const("Добавить ссылку"), id="add_link", state=MainSG.add_link),
        # SwitchTo(Const("Изменить ссылку"), id="edit_link", ),
        Button(Const("Посмотреть ссылки"), id="show_links", on_click=show_links),
        # Button(Const("Удалить ссылку"), id="delete", on_click=delete_link),
        # Group(Const("")),
        parse_mode="markdown",
        state=MainSG.start,
    ),
    Window(
        Const("Введите ссылку"),
        MessageInput(func=add_link),
        Back(Const("Назад")),
        parse_mode="markdown",
        state=MainSG.add_link,
    ),
    # Window(
    #     Format(""),
    #     getter=pass
    # )
]
