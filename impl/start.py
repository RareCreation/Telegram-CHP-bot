from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile, \
    BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import sqlite3
import asyncio
import re
from typing import Dict, Tuple
from PIL import Image
from io import BytesIO

from handlers.bot_instance import dp, bot
from states.form import OnlineCheckState, InstructionState, Form
from utils.check_status_util import check_status
from utils.emails_util import send_email


def init_db():
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracking (
        tg_id INTEGER,
        steam_id TEXT,
        comment TEXT,
        last_status TEXT,
        PRIMARY KEY (tg_id, steam_id)
    )
    ''')

    conn.commit()
    conn.close()


init_db()

tracking_tasks: Dict[Tuple[int, str], asyncio.Task] = {}


@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Письмо", callback_data="send_email")],
            [InlineKeyboardButton(text="📖 Инструкция", callback_data="show_instructions")],
            [InlineKeyboardButton(text="🟢 Check Online", callback_data="online_status")]
        ]
    )
    await message.answer("Выбери одну из функций:", reply_markup=keyboard)


@dp.callback_query(F.data == "send_email")
async def email_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите email, на который отправить письмо:")
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


@dp.callback_query(F.data == "show_instructions")
async def show_instructions(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📖 Отправьте аватарку для обработки",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
            ]
        )
    )
    await state.set_state(InstructionState.waiting_for_avatar)

@dp.message(InstructionState.waiting_for_avatar, F.photo)
async def process_avatar(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    try:
        base_image = Image.open("resources/base.png")
        avatar_image = Image.open(BytesIO(file_bytes.read()))

        avatar_image = avatar_image.resize((85, 85))

        avatar_image_second = avatar_image.resize((100, 100))

        base_image.paste(avatar_image, (1210, 190))

        base_image.paste(avatar_image_second, (1782, 175))

        output_buffer = BytesIO()
        base_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        buffered_file = BufferedInputFile(file=output_buffer.getvalue(), filename="avatar.png")
        await message.answer_photo(photo=buffered_file)

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке изображения: {e}")

    await state.clear()



@dp.callback_query(F.data == "online_status")
async def on_online_status(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Чекер статуса\n╰ уведомляет об изменениях статуса мамонта\n\n"
        "📎 Отправь ссылку на профиль мамонта:\n\n"
        "❗️Внимание: Если вписать ссылку на профиль который вы уже отслеживаете - бот выключит отслеживание данного участника.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
            ]
        )
    )
    await state.set_state(OnlineCheckState.waiting_for_profile_link)


@dp.message(OnlineCheckState.waiting_for_profile_link)
async def handle_online_status_link(message: Message, state: FSMContext):
    url = message.text.strip()
    match = re.fullmatch(r"https?://steamcommunity\.com/profiles/(\d{17})/?", url)

    if not match:
        await message.answer("❌ Ошибка: Неверный формат ссылки. Пример: https://steamcommunity.com/profiles/7656119...")
        return

    steam_id = match.group(1)
    tg_id = message.from_user.id

    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT 1 FROM tracking WHERE tg_id = ? AND steam_id = ?', (tg_id, steam_id))
    if cursor.fetchone():
        cursor.execute('DELETE FROM tracking WHERE tg_id = ? AND steam_id = ?', (tg_id, steam_id))
        conn.commit()

        task_key = (tg_id, steam_id)
        if task_key in tracking_tasks:
            tracking_tasks[task_key].cancel()
            del tracking_tasks[task_key]

        await message.answer(f"❌ Отслеживание профиля {steam_id} остановлено.")
        await state.clear()
        return

    cursor.execute('SELECT COUNT(*) FROM tracking WHERE tg_id = ?', (tg_id,))
    count = cursor.fetchone()[0]

    if count >= 10:
        await message.answer("❌ Вы достигли лимита отслеживаемых профилей (10).")
        await state.clear()
        return

    await state.update_data(steam_id=steam_id, url=url)
    await message.answer("💬 Напишите комментарий для этого профиля:")
    await state.set_state(OnlineCheckState.waiting_for_comment)


@dp.message(OnlineCheckState.waiting_for_comment)
async def handle_profile_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    data = await state.get_data()
    steam_id = data['steam_id']
    url = data['url']
    tg_id = message.from_user.id

    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO tracking (tg_id, steam_id, comment, last_status) VALUES (?, ?, ?, ?)',
                   (tg_id, steam_id, comment, "Currently Offline"))
    conn.commit()
    conn.close()

    task = asyncio.create_task(check_status(tg_id, steam_id, comment))
    tracking_tasks[(tg_id, steam_id)] = task

    await message.answer(f"✅ Отслеживание профиля начато\n\n"
                         f"📎 {url}\n"
                         f"💬 Комментарий: \"{comment}\"")
    await state.clear()


@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Письмо", callback_data="send_email")],
            [InlineKeyboardButton(text="📖 Инструкция", callback_data="show_instructions")],
            [InlineKeyboardButton(text="🟢 Check Online", callback_data="online_status")]
        ]
    )
    await callback.message.edit_text("Выбери одну из функций:", reply_markup=keyboard)


async def restore_tracking_tasks():
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tg_id, steam_id, comment FROM tracking')
    rows = cursor.fetchall()
    conn.close()

    for tg_id, steam_id, comment in rows:
        task = asyncio.create_task(check_status(tg_id, steam_id, comment))
        tracking_tasks[(tg_id, steam_id)] = task
