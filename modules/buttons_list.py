from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='🟥 Red'),
        KeyboardButton(text='🟩 Green'),
        KeyboardButton(text='⬛️ Black')
    )
    builder.row(
        KeyboardButton(text='💲 Daily'),
        KeyboardButton(text='💰 Balance')
    )

    builder.row(
        KeyboardButton(text='📊 Stats'),  # (🛠)
        KeyboardButton(text='📈 Leaders')
    )

    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Что делаем?")


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Что делаем?")


def get_webapp_kb():
    buttons = [
        [
            InlineKeyboardButton(text='Click!', web_app=WebAppInfo(url='https://cocounter.reflex.run/')),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_bet_kb(last=None):
    if last is None:
        last = 100
    buttons = [
        [
            InlineKeyboardButton(text='-10', callback_data='bet_min_10'),

            InlineKeyboardButton(text='Default', callback_data='bet_standard'),
            InlineKeyboardButton(text='+10', callback_data='bet_plus_10')
        ],
        [
            InlineKeyboardButton(text='/2', callback_data='bet_div'),
            InlineKeyboardButton(text=f'{last}', callback_data='bet_now'),
            InlineKeyboardButton(text='x2', callback_data='bet_double')
        ],
        [
            InlineKeyboardButton(text='-100', callback_data='bet_min_100'),
            InlineKeyboardButton(text='All In', callback_data='bet_allin'),
            InlineKeyboardButton(text='+100', callback_data='bet_plus_100')
        ],
        [
            InlineKeyboardButton(text='❌', callback_data='bet_no'),
            InlineKeyboardButton(text='✅', callback_data='bet_yes')
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
