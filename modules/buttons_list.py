from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text='💲 Купить подписку')
    )

    # builder.row(
    #     KeyboardButton(text='⭐️ Тарифы')
    # )

    builder.row(
        # KeyboardButton(text='📊 Статистика'),  # (🛠)
        KeyboardButton(text='❔ Об этом боте'),  # (🛠)
        KeyboardButton(text='👤 Ваш профиль')
    )

    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Что делаем?")


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Что делаем?")


def get_access_kb():
    buttons = [
        [
            InlineKeyboardButton(text='🔒 Получить доступ', callback_data='access_btn')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_rates_kb():
    buttons = [
        [
            InlineKeyboardButton(text='🟡 1 месяц', callback_data='one_month'),
            InlineKeyboardButton(text='🟡 3 месяца', callback_data='three_month')
        ],
        [
            InlineKeyboardButton(text='🟢 1 месяц (+ чат)', callback_data='one_month_prem'),
            InlineKeyboardButton(text='🟢 3 месяца (+ чат)', callback_data='three_month_prem')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_payment_kb():
    buttons = [
        [
            InlineKeyboardButton(text='✅ Отправить скрин / ссылку на транзакцию', callback_data='pending_payment')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_back_kb():
    buttons = [
        [
            InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel_pending_payment')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
