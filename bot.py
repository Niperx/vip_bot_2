import logging
import config
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.storage.memory import MemoryStorage

from modules.commands_list import CMD_LIST
from handlers import common, play, web
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

    dp.include_routers(
        web.router,
        common.router,
        play.router
    )

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
