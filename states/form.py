from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    email = State()
    login = State()
    operator = State()
