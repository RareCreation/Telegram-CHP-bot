from aiogram import F, Router
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
from utils.check_status_util import check_status, tracking_tasks

router = Router(name="start")

def load(dp: Router) -> None:
    dp.include_router(router)


@router.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Инструкция", callback_data="show_instructions")],
            [InlineKeyboardButton(text="🟢 Check Online", callback_data="online_status")],
            [InlineKeyboardButton(text="📋 Check List", callback_data="check_list")]
        ]
    )
    await message.answer("Выбери одну из функций:", reply_markup=keyboard)



@router.callback_query(F.data == "check_list")
async def check_list_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT steam_id, comment, last_status FROM tracking WHERE tg_id = ?', (tg_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await callback.message.edit_text(
            "📋 У тебя пока нет отслеживаемых мамонтов.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
                ]
            )
        )
        return

    text = "📋 Мамонты:\n\n"
    for i, (steam_id, comment, last_status) in enumerate(rows, start=1):
        text += (f"🆔 <code>{steam_id}</code>\n"
                 f"💬 {comment}\n"
                 f"🔵 Статус: {last_status}\n\n")

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
            ]
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Инструкция", callback_data="show_instructions")],
            [InlineKeyboardButton(text="🟢 Check Online", callback_data="online_status")],
            [InlineKeyboardButton(text="📋 Check List", callback_data="check_list")]
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
