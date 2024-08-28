from aiogram.fsm.state import StatesGroup, State


class MainStates(StatesGroup):
    add_url = State()
    edit_url = State()
    confirm_del = State()
