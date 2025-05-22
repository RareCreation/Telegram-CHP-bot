from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.bot_instance import dp
from states.form import Form
from utils.emails_util import send_email

@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Введите email, на который отправить письмо:")
    await state.set_state(Form.email)


@dp.message(Form.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите логин пользователя:")
    await state.set_state(Form.login)

@dp.message(Form.login)
async def get_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите имя оператора поддержки:")
    await state.set_state(Form.operator)


@dp.message(Form.operator)
async def get_operator(message: Message, state: FSMContext):
    data = await state.update_data(operator=message.text)
    await message.answer("Отправляю письмо...")

    await send_email(
        to_email=data["email"],
        login=data["login"],
        operator=data["operator"]
    )
    await message.answer("Письмо отправлено.")
    await state.clear()
