from aiogram import Dispatcher
from tgbot.functions.start import *
from tgbot.functions.user_action import *


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*", content_types=types.ContentType.ANY)
    dp.register_callback_query_handler(user_call_registered, state='*')
    dp.register_message_handler(get_site, state="*", content_types=types.ContentType.ANY)
