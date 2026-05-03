from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
import sqlite3
import asyncio
import re

from states.form import OnlineCheckState
from utils.logger_util import logger
from utils.steam_api import resolve_vanity_url
from utils.check_status_util import check_status, tracking_tasks

router = Router(name="online_status")

def load(dp: Router):
    dp.include_router(router)

@router.callback_query(F.data == "online_status")
async def on_online_status(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Чекер статуса\n\n📎 Отправь ссылку на профиль:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]]
        )
    )
    await state.set_state(OnlineCheckState.waiting_for_profile_link)

@router.message(OnlineCheckState.waiting_for_profile_link)
async def handle_online_status_link(message: Message, state: FSMContext):
    url = message.text.strip()
    steam_id = None

    match_profile = re.fullmatch(r"https?://steamcommunity\.com/profiles/(\d{17})/?", url)
    if match_profile:
        steam_id = match_profile.group(1)

    match_vanity = re.fullmatch(r"https?://steamcommunity\.com/id/([a-zA-Z0-9_-]+)/?", url)
    if match_vanity:
        steam_id = await resolve_vanity_url(match_vanity.group(1))

    if not steam_id:
        await message.answer("❌ Неверная ссылка")
        return
    logger.info(f"Received link: {url}")
    logger.info(f"Resolved steam_id: {steam_id}")
    tg_id = message.from_user.id

    conn = sqlite3.connect("tracking.db")
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM tracking WHERE tg_id = ? AND steam_id = ?", (tg_id, steam_id))
    if cursor.fetchone():
        cursor.execute("DELETE FROM tracking WHERE tg_id = ? AND steam_id = ?", (tg_id, steam_id))
        conn.commit()

        task_key = (tg_id, steam_id)
        if task_key in tracking_tasks:
            tracking_tasks[task_key].cancel()
            del tracking_tasks[task_key]

        await message.answer("❌ Отслеживание остановлено")
        await state.clear()
        return

    cursor.execute("SELECT COUNT(*) FROM tracking WHERE tg_id = ?", (tg_id,))
    if cursor.fetchone()[0] >= 20:
        await message.answer("❌ Лимит 20 профилей")
        await state.clear()
        return

    await state.update_data(steam_id=steam_id, url=url)
    await message.answer("💬 Комментарий:")
    await state.set_state(OnlineCheckState.waiting_for_comment)

@router.message(OnlineCheckState.waiting_for_comment)
async def handle_profile_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    data = await state.get_data()

    steam_id = data["steam_id"]
    url = data["url"]
    tg_id = message.from_user.id

    conn = sqlite3.connect("tracking.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tracking (tg_id, steam_id, comment, last_status) VALUES (?, ?, ?, ?)",
        (tg_id, steam_id, comment, "offline")
    )

    conn.commit()
    conn.close()
    logger.info(f"Saving tracking: tg_id={tg_id}, steam_id={steam_id}, comment={comment}")
    task = asyncio.create_task(check_status(tg_id, steam_id, comment))
    tracking_tasks[(tg_id, steam_id)] = task

    await message.answer(f"✅ Начато отслеживание\n\n{url}\n💬 {comment}")
    await state.clear()