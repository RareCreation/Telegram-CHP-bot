from aiogram import Bot
from aiogram.types import BotCommand

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="▶️ Запуск бота"),
    ]
    await bot.set_my_commands(commands)