import datetime

from telebot import TeleBot, types

from . import commands, messages, callbacks, keyboards
from app import app, db


bot = TeleBot("7043411349:AAExHLfAPfOf5GpN5wfWHYF9sBS30yCAAmo")


@bot.message_handler(func=commands.REG_USER)
def register_user(message: types.Message):
    def _register_user(_message: types.Message):
        if commands.GOBACK(_message):
            main(_message)
            return
        user = app.register_user(_message.text)
        bot.send_message(message.chat.id, messages.USER_WAS_REGISTERED.format(user=user))
        bot.send_message(message.chat.id, user.utoken, reply_markup=keyboards.ADMIN_KB)

    sent = bot.send_message(message.chat.id, messages.CHOICE_USER_NAME, reply_markup=keyboards.GOBACK_KB)
    bot.register_next_step_handler(sent, _register_user)


@bot.message_handler(func=commands.REMOVE_USER)
def get_users_for_remove(message: types.Message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for user in app.all_users():
        kb.add(types.InlineKeyboardButton(user.name, callback_data=callbacks.REMOVE_USER.send_data(str(user.id))))
    bot.send_message(message.chat.id, messages.CHOICE_USER_NAME, reply_markup=kb)


@bot.callback_query_handler(func=callbacks.REMOVE_USER)
def remove_user(callback: types.CallbackQuery):
    if (user := app.remove_user(*callbacks.get_data(callback))) is not None:
        bot.send_message(callback.message.chat.id, messages.USER_IS_REMOVED.format(user=user))


@bot.message_handler(func=commands.GET_ADMIN_HOURS_REPORT)
def get_admin_hours_report_months(message: types.Message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for month in app.work_months():
        kb.add(types.InlineKeyboardButton(month, callback_data=callbacks.ADMIN_HOURS_REPORT.send_data(month)))
    bot.send_message(message.chat.id, messages.CHOICE_MONTH_FOR_REPORT, reply_markup=kb)


@bot.callback_query_handler(func=callbacks.ADMIN_HOURS_REPORT)
def get_admin_hours_report(callback: types.CallbackQuery):
    report = app.create_admin_hours_report(*(int(x) for x in callbacks.get_data(callback)[0].split('.')))
    with open(report, 'rb') as report:
        bot.send_document(callback.message.chat.id, report, reply_markup=keyboards.ADMIN_KB)


@bot.message_handler(func=commands.CORRECT_TIME)
def get_users_for_correct(message: types.Message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for user in app.all_users():
        kb.add(types.InlineKeyboardButton(user.name, callback_data=callbacks.CORRECT_USER.send_data(str(user.id))))
    bot.send_message(message.chat.id, messages.CHOICE_USER_NAME, reply_markup=kb)


@bot.callback_query_handler(func=callbacks.CORRECT_USER)
def get_days_for_correct(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(row_width=1)
    user = app.user_by_id(*callbacks.get_data(callback))
    for work_day in app.correctable_work_day(user.id):
        kb.add(types.InlineKeyboardButton(
            f"{work_day.day.strftime('%d.%m.%Y')}: {work_day.time}",
            callback_data=callbacks.CORRECT_TIME.send_data(str(work_day.user_id), work_day.day.strftime('%Y.%m.%d'))))
    bot.send_message(callback.message.chat.id, messages.CHOICE_DATE_TO_CORRECT.format(user=user), reply_markup=kb)


@bot.callback_query_handler(func=callbacks.CORRECT_TIME)
def correct_day(callback: types.CallbackQuery):
    def _correct_day(_message: types.Message):
        if commands.GOBACK(_message):
            main(_message)
            return
        if not (_message.text.count('.') <= 1 and _message.text.replace('.', '').isdigit()):
            bot.send_message(_message.chat.id, messages.INVALID_TIME)
            main(_message)
            return
        user_id, date = callbacks.get_data(callback)
        app.correct_day(user_id, datetime.date(*map(int, date.split('.'))), float(_message.text))
        bot.send_message(_message.chat.id, messages.TIME_WAS_CORRECTED, reply_markup=keyboards.ADMIN_KB)

        kb = types.InlineKeyboardMarkup(row_width=1)
        for work_day in app.correctable_work_day(user_id):
            kb.add(types.InlineKeyboardButton(
                f"{work_day.day.strftime('%d.%m.%Y')}: {work_day.time}",
                callback_data=callbacks.CORRECT_TIME.send_data(str(work_day.user_id),
                                                               work_day.day.strftime('%Y.%m.%d'))))
        bot.edit_message_text(callback.message.text, _message.chat.id, callback.message.id, reply_markup=kb)

    sent = bot.send_message(callback.message.chat.id, messages.ENTER_NEW_TIME, reply_markup=keyboards.GOBACK_KB)
    bot.register_next_step_handler(sent, _correct_day)


@bot.message_handler(func=commands.FIX_TIME)
def fix_time(message: types.Message):
    if isinstance((fix_time_model := app.fix_time(message.from_user.id)), db.UserTimeInModel):
        bot.send_message(message.chat.id, messages.SHIFT_WAS_STARTED.format(fix_time_model=fix_time_model),
                         reply_markup=keyboards.USER_KB)
        for admin in app.all_admins():
            bot.send_message(admin.chat_id, messages.USER_STARTED_SHIFT.format(fix_time_model=fix_time_model))
    else:
        bot.send_message(message.chat.id, messages.SHIFT_WAS_FINISHED.format(fix_time_model=fix_time_model),
                         reply_markup=keyboards.USER_KB)
        for admin in app.all_admins():
            bot.send_message(admin.chat_id, messages.USER_FINISHED_SHIFT.format(fix_time_model=fix_time_model))


@bot.message_handler(func=commands.GET_WORKER_HOURS_REPORT)
def get_work_months(message: types.Message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for months in app.user_work_months(message.from_user.id):
        kb.add(types.InlineKeyboardButton(months, callback_data=callbacks.USER_HOURS_REPORT.send_data(months)))
    bot.send_message(message.chat.id, messages.CHOICE_MONTH_FOR_REPORT, reply_markup=kb)


@bot.callback_query_handler(func=callbacks.USER_HOURS_REPORT)
def get_user_hours_report(callback: types.CallbackQuery):
    bot.send_message(
        callback.message.chat.id,
        '\n'.join(f"{work_day.day.strftime('%d.%m.%Y')}: {work_day.time}" for work_day in app.get_user_hours(
            callback.from_user.id, *map(int, callbacks.get_data(callback)[0].split('.'))))
    )


@bot.message_handler(commands=["start"])
def start(message: types.Message):
    if app.is_new_tg_user(message.from_user.id):
        for admin in app.all_admins():
            bot.send_message(admin.chat_id, messages.NOTIFY_ADMIN_ABOUT_NEW_USER.format(message=message))
    else:
        main(message)


@bot.message_handler()
def main(message: types.Message):
    print('message from chat_id:', message.chat.id)
    if app.verificate_admin(message.chat.id):
        bot.send_message(message.chat.id, messages.WELCOME_ADMIN, reply_markup=keyboards.ADMIN_KB)

    elif user := app.verificate_user(message.from_user.id):
        bot.send_message(message.chat.id, messages.WELCOME_USER.format(user=user), reply_markup=keyboards.USER_KB)

    elif user := app.reg_tg_user(message.text, message.from_user.id):
        for admin in app.all_admins():
            bot.send_message(admin.chat_id, messages.USER_FINISHED_REGISTERING.format(user=user, message=message))
        bot.send_message(message.chat.id, messages.REGISTER_WAS_FINISHED_SUCCESS)
        main(message)
