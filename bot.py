import asyncio
import logging
from pathlib import Path
from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.bot.api import TelegramAPIServer


from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
from tgbot.handlers.download_handler import register_download_handler

from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.i18n import CustomI18nMiddleware
from tgbot.middlewares.check import CheckSubscriptionMiddleware

from tgbot.misc.set_bot_commands import set_default_commands
from tgbot.services.db import db
import aioschedule

logger = logging.getLogger(__name__)

schedule_update_credits = aioschedule.Scheduler()


BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR /'locales/'
i18n = CustomI18nMiddleware(config=load_config(".env"), domain="savebot", path=LOCALES_DIR)

async def scheduler():
    schedule_update_credits.every().day.at("5:00").do(db.update_credits)
    while True:
        await schedule_update_credits.run_pending()
        await asyncio.sleep(1)

def register_all_middlewares(dp, config):
    dp.setup_middleware(CheckSubscriptionMiddleware())
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(CustomI18nMiddleware(config=load_config(".env"), domain="savebot", path=LOCALES_DIR))
    

def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_download_handler(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    # Create private Bot API server endpoints wrapper
    local_server = TelegramAPIServer.from_base(config.tg_bot.base_url)

    # bot config
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, server=local_server, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    bot['config'] = config

    # create db
    await db.create()

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    asyncio.create_task(scheduler())

    await set_default_commands(bot)
    
    # await bot.log_out()
    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
