from aiogram.fsm.state import StatesGroup, State


class MainSG(StatesGroup):
    start = State
    add_link = State
    edit_link = State
    show_link = State
    delete_link = State
