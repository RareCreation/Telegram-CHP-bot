import asyncio
from handlers.bot_instance import dp, bot
from impl.start import init_db
from utils.logger_util import logger
from impl import start
from utils.setup_commands import setup_bot_commands


async def main():
    logger("Bot has been launched")
    await setup_bot_commands(bot)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    init_db()

    asyncio.run(main())
