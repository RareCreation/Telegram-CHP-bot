from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

router = Router(name="check_list")

def load(dp: Router):
    dp.include_router(router)

@router.callback_query(F.data == "check_list")
async def check_list_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id

    conn = sqlite3.connect("tracking.db")
    cursor = conn.cursor()
    cursor.execute("SELECT steam_id, comment, last_status FROM tracking WHERE tg_id = ?", (tg_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await callback.message.edit_text(
            "📋 Пусто",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]]
            )
        )
        return

    text = "📋 Список:\n\n"

    for steam_id, comment, last_status in rows:
        text += f"🆔 {steam_id}\n💬 {comment}\n🔵 {last_status}\n\n"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]]
        )
    )