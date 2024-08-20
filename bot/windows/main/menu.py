from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from bot.states.main import MainSG

MainMenuWin = [
    Window(
        Const(
            """
        Доброго времени суток. С вами на связи *SLBot*
        Высылаю вам клавиатуру для взаимодействия с нашим софтом
        """
        ),
        Button(Const("Добавить ссылку"), on_click=None),
        Button(Const("Изменить ссылку")),
        Button(Const("Посмотреть ссылки")),
        Button(Const("Удалить ссылку")),
        parse_mode="markdown",
        state=MainSG.start,
    ),
]
