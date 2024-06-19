from telebot import types


class _Callback:
    def __call__(self, callback: types.CallbackQuery):
        return int(callback.data.split('&')[0]) == id(self)

    def send_data(self, *data: str):
        return f"{id(self)}&{'&'.join(data)}"


def get_data(callback: types.CallbackQuery):
    return callback.data.split('&')[1:]


USER_HOURS_REPORT = _Callback()
CORRECT_TIME = _Callback()
CORRECT_USER = _Callback()
ADMIN_HOURS_REPORT = _Callback()
REMOVE_USER = _Callback()
