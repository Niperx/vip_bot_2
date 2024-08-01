# coding=utf-8
import asyncio
import logging
import os.path
import aiogram.types

from aiogram import Bot, types, Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link

from db.db_manage import *
from config import TOKEN

from modules import admins_list
from modules.buttons_list import *
from modules.chat_type import ChatTypeFilter

bot = Bot(token=TOKEN)
router = Router()

admin = admins_list.ADMINS[1]


class PaymentStage(StatesGroup):
    waiting_for_pending = State()


async def get_logs(text, username='Anonim', name='Anonim'):
    now = datetime.now()
    now_file = datetime.strftime(now, '%d_%m')
    now_info = datetime.strftime(now, '%d.%m %H:%M:%S')
    logs_text = ''
    if os.path.isfile(f"logs/logs_{now_file}.txt"):
        with open(f"logs/logs_{now_file}.txt", "r", encoding="utf-8") as read_logs:
            logs_text = read_logs.read()

    logs_text = logs_text + f'## {now_info} ## @{username} ({name}) {text}\n'

    with open(f"logs/logs_{now_file}.txt", "w", encoding="utf-8") as write_logs:
        write_logs.write(logs_text)


async def get_info_about_user_message(message):  # Инфа о сообщении в консоль
    text = f'\n##### {datetime.now()} #####\n'
    text += f'ID: {message.from_user.id}, Text: {message.text}, Chat ID: {message.chat.id}'
    try:
        text += f'\nUsername: {message.from_user.username},' \
                f' Name: {message.from_user.first_name},' \
                f' Surname: {message.from_user.last_name} '
    except Exception as e:
        logging.exception(e)
        text += 'Нет имени'
    return text


async def get_info_about_user_callback(callback):  # Инфа о коллбеке в консоль
    text = f'\n##### {datetime.now()} #####\n'
    text += f'ID: {callback.from_user.id}, Text: {callback.data}'
    try:
        text += f'\nUsername: {callback.from_user.username},' \
                f' Name: {callback.from_user.first_name},' \
                f' Surname: {callback.from_user.last_name} '
    except Exception as e:
        logging.exception(e)
        text += 'Нет имени'
    return text


@router.message(ChatTypeFilter(chat_type=["private"]), Command(commands=["start"]))
@router.message(CommandStart(deep_link=True))
async def cmd_start(message: types.Message, command: CommandObject):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text = 'Добро пожаловать в помощника для трейдинга, более подробно об этом боте мы рассказали в видео:\nhttps://youtu.be/Gnpx6p-xMjU'

    user_id = message.from_user.id
    chk = await check_user_id(user_id)
    if not chk:
        balance = START_BONUS
        code = command.args
        if code is not None and code.isdigit() and code != message.from_user.id:
            chk_ref = await check_user_id(int(code))
            if not chk_ref:
                code = None
            else:
                code = int(code)
                balance += REF_INV_BONUS
                if message.from_user.username is not None:
                    await bot.send_message(chat_id=code,
                                           text=f'У вас новый реферал {message.from_user.first_name}'
                                                f' - @{message.from_user.username}')
                else:
                    await bot.send_message(chat_id=code,
                                           text=f'У вас новый реферал {message.from_user.first_name}')
                await add_money(code, balance)
            text += f'\n<i>(Ваш бонус: ${balance} по реферальной системе)</i>'
        await create_user(user_id, message.from_user.username, balance, code)
        text += '\n<i>(Ваш аккаунт успешно создан)</i>'

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(Command(commands=["about"]))
@router.message(F.text == '❔ Об этом боте')
async def cmd_profile(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text = f"Эти зоны покупок и продаж это алгоритм, который создал мой товарищ и трейдер с огромным стажем, " \
           f"этот алгоритм не имеет никакого аналога в интернете, для тех кому интересно - они не основаны на индикаторах как у всех, и это не зоны поддержки-сопротивления.\n" \
           f"Они основаны на нескольких вещах:\n" \
           f"Математические закономерности фракталы и реальные биржевые объемы.\n" \
           f"Полную информацию конечно же никто не даст, но думаю что важнее то что это реально отрабатывает каким-то фантастическим чудом, а не то по какому принципу оно работает.\n\n" \
           f"Поддержка бота - @cryptolog_admin"

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(Command(commands=["profile"]))
@router.message(F.text == '👤 Ваш профиль')
async def cmd_profile(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text = f'👤 {message.from_user.first_name}\n\n' \
           f'<b>Активные подписки:</b>\n'
    payment_time = await check_payment_time(message.from_user.id)

    if payment_time < 0:
        text += f'💳 Нет подписок'
    else:
        days = round(payment_time / 60 / 60 / 24)
        days_end = datetime.today() + timedelta(days=1)
        text += f"💳 Осталось дней подписки: {days} ({days_end.strftime('%a, %d %b %Y')})\n\n"
        # text += 'Доступы: \n' \
        #         'Раз - \n' \
        #         'Два - '

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(Command(commands=["stats"]))
@router.message(F.text == '📊 Статистика')
async def cmd_profile(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    stats = await get_stats_all()
    one, three, one_prem, three_prem = stats[0], stats[1], stats[2], stats[3]

    buyers = await count_users_buyers()
    buyers_month = await get_stats_of_month()

    full_money = one * RATES['one'] + three * RATES['three'] + one_prem * RATES['one_prem'] + three_prem * RATES['three_prem']
    month_money = buyers_month[0] * RATES['one'] + buyers_month[1] * RATES['three'] + buyers_month[2] * RATES['one_prem'] + buyers_month[3] * RATES['three_prem']

    users = await count_users()

    text = f'<b>Статистика:</b>\n\n' \
           f'Кол-во пользователей: {users}\n' \
           f'Кол-во покупателей: {buyers}\n\n' \
           f'На сколько месяцев куплено (без чата):\n' \
           f'-- 1 месяц: {one}\n' \
           f'-- 3 месяца: {three}\n\n' \
           f'На сколько месяцев куплено (с чатом):\n' \
           f'-- 1 месяц: {one_prem}\n' \
           f'-- 3 месяца: {three_prem}\n\n' \
           f'Прибыль за месяц: ${month_money}\n' \
           f'Прибыль всего: ${full_money}\n'

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(Command(commands=["balance"]))
@router.message(F.text == '💰 Balance')
async def cmd_check_balance(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    user_id = message.from_user.id
    balance = await get_balance(user_id)
    text = (f'🪙 <b>Ваш баланс:</b> 🪙\n'
            f'{int(balance)}')
    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(f'проверил свой баланс на сумму {int(balance)} коинов', message.from_user.username,
                   message.from_user.first_name)


@router.message(Command(commands=["clear"]))
async def cmd_check_stats(message: types.Message):
    a = await message.answer('Клавиатура удалена', reply_markup=aiogram.types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await a.delete()
