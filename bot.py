import datetime
import logging
import config
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler


from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.storage.memory import MemoryStorage

from modules.commands_list import CMD_LIST
from handlers import common, buy
from db.db_manage import check_db

bot = Bot(token=config.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
main_router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):  # Загрузка команд из файлика
    commands = []

    for cmd in CMD_LIST:
        commands.append(types.BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands)


async def main():
    # await check_db()  # Проверка на существование ДБ

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    # scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # scheduler.add_job(buy.check_subscribe, trigger='interval', seconds=20)
    # scheduler.start()

    dp.include_routers(
        common.router,
        buy.router
    )
    # dp.startup.register(on_startup)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())
