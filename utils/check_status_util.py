import asyncio
import sqlite3

import requests
from bs4 import BeautifulSoup

from handlers.bot_instance import bot


async def check_status(tg_id: int, steam_id: str, comment: str):
    url = f"https://steamcommunity.com/profiles/{steam_id}/"
    last_status = None

    while True:
        try:
            conn = sqlite3.connect('tracking.db')
            cursor = conn.cursor()

            cursor.execute('SELECT 1 FROM tracking WHERE tg_id = ? AND steam_id = ?', (tg_id, steam_id))
            if not cursor.fetchone():
                break

            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            persona_name_element = soup.find("span", class_="actual_persona_name")
            persona_name = persona_name_element.text.strip() if persona_name_element else "Неизвестный пользователь"

            status_element = soup.find("div", class_="profile_in_game_header")
            current_status = status_element.text.strip() if status_element else "Currently Offline"

            simplified_status = "Currently Online" if "in-game" in current_status.lower() or "online" in current_status.lower() else "Currently Offline"

            cursor.execute('SELECT last_status FROM tracking WHERE tg_id = ? AND steam_id = ?', (tg_id, steam_id))
            row = cursor.fetchone()
            db_last_status = row[0] if row else None

            if db_last_status != simplified_status:
                cursor.execute('UPDATE tracking SET last_status = ? WHERE tg_id = ? AND steam_id = ?',
                               (simplified_status, tg_id, steam_id))
                conn.commit()

                if simplified_status == "Currently Online":
                    message = (
                        "🟢 Мамонт зашёл в сеть\n\n"
                        f"🪪 {persona_name}\n"
                        f"💬 \"{comment}\"\n"
                        f"📎 {url}"
                    )
                else:
                    message = (
                        "🔴 Мамонт вышел из сети\n\n"
                        f"🪪 {persona_name}\n"
                        f"💬 \"{comment}\"\n"
                        f"📎 {url}"
                    )

                await bot.send_message(tg_id, message)

            await asyncio.sleep(30)

        except Exception as e:
            print(f"[ERROR] Ошибка при проверке статуса: {e}")
            await asyncio.sleep(60)
        finally:
            conn.close()
