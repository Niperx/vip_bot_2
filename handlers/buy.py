# coding=utf-8
import logging
import os.path
import asyncio

from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command

from db.db_manage import *
from config import TOKEN

from modules import admins_list
from modules.buttons_list import *
from modules.chat_type import ChatTypeFilter, IsAdmin

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


@router.message(Command(commands=["get"]))
async def cmd_profile(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    await update_payment_time(message.from_user.id, 1)


@router.message(Command(commands=["buy"]))
@router.message(F.text == '💲 Купить подписку')
async def cmd_access(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text = f'Условия вступления\n\n' \
           f'🟠 1 месяц -- ${RATES["one"]}\n' \
           f'🟡 3 месяца -- ${RATES["three"]}\n' \
           f'🟢 6 месяцев -- ${RATES["six"]}'

    await message.answer(text, reply_markup=get_access_kb(), parse_mode='HTML')


@router.callback_query(F.data == 'access_btn')
async def process_benefit(callback: types.CallbackQuery):
    print(await get_info_about_user_callback(callback))
    text = '🤘 Выберите необходимый вам тариф:'
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_rates_kb())


@router.callback_query(F.data == 'one_month')
@router.callback_query(F.data == 'three_month')
@router.callback_query(F.data == 'six_month')
async def process_month(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    await state.update_data(plan=callback.data)

    value = 0

    print(callback.data)

    match callback.data:
        case 'one_month':
            value = RATES["one"]
        case 'three_month':
            value = RATES["three"]
        case 'six_month':
            value = RATES["six"]

    text = f'Оплатите {value} USDT на любой из кошельков и прикрепите скриншот, либо ссылку на транзакцию.\n\n' \
           f"BEP20 USDT : \n<code>0xEc61937B68f04EFF930D640b508E13fb0E78cC94</code>\n"\
           f"TRC20 USDT : \n<code>TK2YFi2GnXgN7k4FF8g7LDz3LyAepEHcFA</code>"

    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_payment_kb())


@router.callback_query(F.data == 'pending_payment')
async def process_benefit(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    text = f"Ожидание платежа...\n\n"\
           f"❗️ ПРИКРЕПИТЕ ФОТО ЧЕКА ЛИБО ССЫЛКУ ❗️\n\n"\
           f'Нажмите на кнопку "⬅️ Назад", если что-то пошло не так или вы передумали'
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=get_back_kb())

    await state.set_state(PaymentStage.waiting_for_pending)


@router.callback_query(F.data == 'cancel_pending_payment')
async def process_benefit(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    await callback.message.delete()
    await state.set_state(None)


# получить фото и сообщить админу
@router.message(PaymentStage.waiting_for_pending, F.photo)
async def cmd_get_photo(message: types.Message, state: FSMContext):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    user_data = await state.get_data()

    text = 'Спасибо за информацию, подтверждаем транзакцию от администратора, ожидайте...'

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')

    plan = ''

    match user_data['plan']:
        case 'one_month':
            plan = '1 месяц'
        case 'three_month':
            plan = '3 месяца'
        case 'six_month':
            plan = '6 месяцев'

    await bot.send_message(admin,
                           f"Попытка оплаты подписки на *{plan.upper()}*\n\n"
                           f'Возможности:\n"+1" _- 1 месяц_, "+3" _- 3 месяца_, "+6" _- 6 месяцев_\n\n'
                           f'Сообщение от пользователя [{message.from_user.id}](tg://user?id{message.from_user.id}) - 👤 [{message.from_user.first_name}](https://t.me/{message.from_user.username}):',
                           parse_mode='Markdown')

    await bot.forward_message(admin, from_chat_id=message.chat.id, message_id=message.message_id)

    await state.set_state(None)


@router.message(ChatTypeFilter(chat_type=["private"]), IsAdmin(admin_ids=admins_list.ADMINS), F.text.startswith('+'))
async def cmd_get_confirmation(message: types.Message, state: FSMContext):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text_access = 'Доступы: \n\n'\
                  'Чат - 123 \n'\
                  'Канал - 123'

    confirmation = message.text

    match confirmation[1:]:
        case '1':
            print('YES1')
            await update_payment_time(message.reply_to_message.forward_from.id, 1)
            await change_stats('one')
            await bot.send_message(message.reply_to_message.forward_from.id,
                                   '👌 Платеж подтвержден. Вы приобрели подписку на 1 месяц.\n\n' + text_access,
                                   reply_markup=get_menu_kb())
            try:
                await bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.reply_to_message.forward_from.id)
            except:
                pass
            await message.answer('Одобрено на 1 месяц')
        case '3':
            print('YES3')
            await update_payment_time(message.reply_to_message.forward_from.id, 3)
            await change_stats('three')
            await bot.send_message(message.reply_to_message.forward_from.id,
                                   '👌 Платеж подтвержден. Вы приобрели подписку на 3 месяца.\n\n' + text_access,
                                   reply_markup=get_menu_kb())
            try:
                await bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.reply_to_message.forward_from.id)
            except:
                pass
            await message.answer('Одобрено на 3 месяца')
        case '6':
            print('YES6')
            await update_payment_time(message.reply_to_message.forward_from.id, 6)
            await change_stats('six')
            await bot.send_message(message.reply_to_message.forward_from.id,
                                   '👌 Платеж подтвержден. Вы приобрели подписку на 6 месяцев.\n\n' + text_access,
                                   reply_markup=get_menu_kb())
            try:
                await bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.reply_to_message.forward_from.id)
            except:
                pass
            await message.answer('Одобрено на 6 месяцев')
        case _:
            print('Error confrimation')
            await message.answer('Не получилось одобрить, ошибка в тексте, попробуйте ещё раз')


@router.message(ChatTypeFilter(chat_type=["private"]), IsAdmin(admin_ids=admins_list.ADMINS), F.text == '-')
async def cmd_get_confirmation(message: types.Message, state: FSMContext):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    await message.answer('Отменил запрос')

    print('NO')
    await bot.send_message(message.reply_to_message.forward_from.id,
                           'Мы не смогли проверить вашу оплату, свяжитесь с нами: @cryptolog_admin')


async def check_subscribe():
    all_users = await get_users_list()

    for user in all_users:
        try:
            payment_time = await check_payment_time(user[0])
            member_status = await bot.get_chat_member(GROUP_ID, user[0])
            print(type(member_status), user[0])

            if payment_time < 0 \
                    and user[0] not in admins_list.ADMINS \
                    and not isinstance(member_status, types.ChatMemberAdministrator) \
                    and not isinstance(member_status, types.ChatMemberOwner):

                await bot.ban_chat_member(chat_id=GROUP_ID, user_id=user[0])
                if isinstance(member_status, types.ChatMemberMember):
                    await bot.send_message(user[0], 'Ваша подписка закончилась, чтобы продолжить пользоваться услугами, можете купить подписку снова!')
        except:
            continue




# async def get_test():
#     print('testycal')
#
#
# async def scheduler():
#     aioschedule.every(15).seconds.do(get_test)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)


# async def scheduler():
#     aioschedule.every().day.at("12:00").do(check_subscribe)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)


@router.message(Command(commands=["test"]))
async def cmd_access(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    a = datetime.now().month
    print(a)
    print(type(a))
