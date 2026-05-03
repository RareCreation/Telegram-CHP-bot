import asyncio
from handlers.bot_instance import dp, bot
from utils.check_status_util import restore_tracking
from utils.database import init_db, init_users_db
from utils.load_routers import load_routers
from utils.logger_util import logger
from utils.setup_commands import setup_bot_commands


async def main():
    logger.info("Initializing databases...")
    init_db()
    init_users_db()

    await setup_bot_commands(bot)

    await load_routers(dp=dp, bot=bot)
    logger.info("routers loaded")
    await restore_tracking()
    logger.info("Starting bot...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())