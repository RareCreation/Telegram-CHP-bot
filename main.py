import asyncio
from handlers.bot_instance import dp, bot
from utils.logger_util import logger
from impl import start

async def main():
    logger("Bot has been launched")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
