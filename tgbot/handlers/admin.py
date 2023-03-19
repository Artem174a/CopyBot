from aiogram import Dispatcher
from tgbot.functions.start import *


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
