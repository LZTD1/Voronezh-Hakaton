from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

class keyboards():
    def mainKeyboard(self, role):
        #  0(user teamlid), 1 - predstavitel, 2 - admin, 3 partner
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        if role == 0:
            markup.row(KeyboardButton("👥 Моя команда"), KeyboardButton("💥 Мои мероприятия"))
            markup.row(KeyboardButton("💬 Помощь"))
        if role == 1: # Представитель
            markup.row(KeyboardButton("Мои мероприятия"))
            markup.row(KeyboardButton("💬 Помощь"))
        if role == 2:
            markup.row(KeyboardButton("Резюме БД"), KeyboardButton("Предстоящие мероприятия"))
            markup.row(KeyboardButton("💬 Помощь"))
        if role == 3:
            markup.row(KeyboardButton("Спонсированные"), KeyboardButton("Представляю"))
            markup.row(KeyboardButton("💬 Помощь"))
        return markup