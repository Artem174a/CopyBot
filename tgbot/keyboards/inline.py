from aiogram import types, bot
from tgbot.database.DB import Database as Db


class InlineKeyboard:
    def __init__(self):
        self.inline_keyboard = types.InlineKeyboardMarkup
        self.button = types.InlineKeyboardButton
        pass

    def menu(self, ):
        buttons = [
            self.button(text="Баланс", callback_data="get_balance"),
            self.button(text="Купить", callback_data="buy"),
            self.button(text="Скопировать блок", callback_data="copy_block"),
            self.button(text="Инструкция", callback_data="info"),
        ]
        keyboard = self.inline_keyboard()
        keyboard.row(buttons[0], buttons[1])
        keyboard.add(buttons[2])
        keyboard.add(buttons[3])
        return keyboard
