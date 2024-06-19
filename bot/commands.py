from telebot import types
from app import app


class _Command:
    def __init__(self, text: str, admin_permission: bool = None):
        self._text = text
        self._admin_permission = admin_permission

    def __call__(self, message: types.Message):
        return message.text == self._text and (self._admin_permission is None or
                                               app.verificate_admin(message.chat.id) == self._admin_permission)

    @property
    def text(self):
        return self._text


GOBACK = _Command("⬅️ Вернуться")

REG_USER = _Command("✅ Зарегистрировать пользователя", admin_permission=True)
REMOVE_USER = _Command("❎ Удалить пользователя", admin_permission=True)
GET_ADMIN_HOURS_REPORT = _Command("📅 Отчет рабочего времени", admin_permission=True)
CORRECT_TIME = _Command("✏️ Корректировать время", admin_permission=True)

GET_WORKER_HOURS_REPORT = _Command("📅 Отчет по своим часам", admin_permission=False)
FIX_TIME = _Command("⏰Зафиксировать время", admin_permission=False)
