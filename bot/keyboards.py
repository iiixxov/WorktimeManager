from telebot import types
from . import commands


ADMIN_KB = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
ADMIN_KB.add(
    types.KeyboardButton(commands.REG_USER.text),
    types.KeyboardButton(commands.REMOVE_USER.text),
    types.KeyboardButton(commands.GET_ADMIN_HOURS_REPORT.text),
    types.KeyboardButton(commands.CORRECT_TIME.text)
)

USER_KB = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
USER_KB.add(
    types.KeyboardButton(commands.FIX_TIME.text),
    types.KeyboardButton(commands.GET_WORKER_HOURS_REPORT.text),
)

GOBACK_KB = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
GOBACK_KB.add(
    types.KeyboardButton(commands.GOBACK.text),
)

ANY_KB = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
ANY_KB.add(
    types.KeyboardButton(commands.GOBACK.text),
    types.KeyboardButton(commands.REG_USER.text),
    types.KeyboardButton(commands.REMOVE_USER.text),
    types.KeyboardButton(commands.GET_ADMIN_HOURS_REPORT.text),
    types.KeyboardButton(commands.CORRECT_TIME.text),
    types.KeyboardButton(commands.FIX_TIME.text),
    types.KeyboardButton(commands.GET_WORKER_HOURS_REPORT.text),
)
