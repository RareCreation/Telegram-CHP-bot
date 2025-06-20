from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    email = State()
    login = State()
    operator = State()

class OnlineCheckState(StatesGroup):
    waiting_for_profile_link = State()
    waiting_for_comment = State()
    
class InstructionState(StatesGroup):
    waiting_for_avatar = State()