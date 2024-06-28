# coding=utf-8
import asyncio
import logging
import os.path
import aiogram.types

from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link

from db.db_manage import *
from config import TOKEN

from modules.buttons_list import *
from modules.chat_type import ChatTypeFilter

bot = Bot(token=TOKEN)
router = Router()


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

    text = 'Добро пожаловать в <b>Сигналы</b>'

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
        text += f'💳 Осталось дней подписки: {round(payment_time / 60 / 60 / 24)}\n\n'
        text += 'Доступы: \n' \
                'Раз - \n' \
                'Два - '

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
    print(payment_time)
    # await message.answer(money_time)


@router.message(Command(commands=["get"]))
async def cmd_profile(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    await update_payment_time(message.from_user.id, 1)


@router.message(Command(commands=["rates"]))
@router.message(F.text == '⭐️ Тарифы')
async def cmd_access(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text = f'Условия вступления\n\n' \
           f'🟠 1 месяц -- $100\n' \
           f'🟡 3 месяца -- $300\n' \
           f'🟢 12 месяцев -- $1200'

    await message.answer(text, reply_markup=get_access_kb(), parse_mode='HTML')


@router.callback_query(F.data == 'access_btn')
async def process_benefit(callback: types.CallbackQuery):
    print(await get_info_about_user_callback(callback))
    text = '🤘 Выберите необходимый вам тариф:'
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_rates_kb())


@router.callback_query(F.data == 'one_month')
@router.callback_query(F.data == 'three_month')
@router.callback_query(F.data == 'twelve_month')
async def process_month(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    await state.update_data(plan=callback.data)

    value = 0

    print(callback.data)

    match callback.data:
        case 'one_month':
            value = 100
        case 'three_month':
            value = 300
        case 'twelve_month':
            value = 1200

    text = f'Оплатите {value} USDT на любой из кошельков и прикрепите скриншот, либо ссылку на транзакцию.\n\n' \
           f"ERC20 USDT : \n<code>0x1b7C958510cE37D71Ee0e2F7aB13783D41bf4E6a</code>\n"\
           f"BEP20 USDT : \n<code>0x1b7C958510cE37D71Ee0e2F7aB13783D41bf4E6a</code>\n"\
           f"BEP20 BUSD : \n<code>0x1b7C958510cE37D71Ee0e2F7aB13783D41bf4E6a</code>\n"\
           f"TRC20 USDT : \n<code>TTg3Sv8dpgjhBeAixA4t2RgSBrqaJ3dmJw</code>"

    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_payment_kb())


@router.callback_query(F.data == 'pending_payment')
async def process_benefit(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    text = f"Ожидание платежа...\n\n"\
           f"❗️ ПРИКРЕПИТЕ ФОТО ЧЕКА ЛИБО ССЫЛКУ ❗️\n\n"\
           f'Нажмите на кнопку "⬅️ Назад", если что-то пошло не так или вы передумали'
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_kb())

    await state.set_state(PaymentStage.waiting_for_pending)


# получить фото и сообщить админу


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


@router.message(Command(commands=["leaders"]))
@router.message(F.text == '📈 Leaders')
async def cmd_check_leaders(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    lead_text = f"⭐️ <b>ТОП-{LEADERS_LIST} богатейших людей этого чёртово казино!</b> ⭐️️ \n\n"
    tops_db = await get_leaders(LEADERS_LIST)

    i = 0
    for top in tops_db:
        i += 1
        smile = ''
        if i <= 3:
            match i:
                case 1:
                    smile = '🥇 '
                case 2:
                    smile = '🥈 '
                case 3:
                    smile = '🥉 '
        else:
            smile = '🎗 '
        you_mark = ''
        if message.from_user.username == top[0]:
            you_mark = '(You)'

        lead_text += f'{smile} {i}. @{top[0]} - {int(top[1])} коинов. {you_mark}\n'

    await message.answer(lead_text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(f'посмотрел список лидеров', message.from_user.username, message.from_user.first_name)


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == '📊 Stats')
async def cmd_check_stats(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    user_id = message.from_user.id
    link = await create_start_link(bot, f'{user_id}')
    text = f'<b>Ваша реферальная ссылка:</b> <i>(кликабельно)</i>\n <code>{link}</code>\n\n'

    stats = await get_stats()
    red, green, black = stats[0], stats[1], stats[2]

    text += (f'📊 <b>Статистика:</b> 📊\n\n'
             f'🟥 Красный цвет выпал {red} раз(а) 🟥 ({round(red / (red + green + black) * 100)}%)\n\n'
             f'🟩 Зелёный цвет выпал {green} раз(а) 🟩 ({round(green / (red + green + black) * 100)}%)\n\n'
             f'⬛️ Чёрный цвет выпал {black} раз(а) ⬛️ ({round(black / (red + green + black) * 100)}%)\n\n'
             f'Общее число бросков - {red + green + black} раз(а)')

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(f'посмотрел статистику рандома', message.from_user.username, message.from_user.first_name)


@router.message(Command(commands=["clear"]))
async def cmd_check_stats(message: types.Message):
    a = await message.answer('Клавиатура удалена', reply_markup=aiogram.types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await a.delete()
