from aiogram.types import Message, Contact
from tgbot.database.DB import Database as Db
from tgbot.keyboards.inline import *


async def admin_start(message: Message):
    await message.reply("Hello, admin!")


def sklonenie_blocks(number):
    if number % 10 == 1 and number % 100 != 11:
        return f"{number} бесплатный блок"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return f"{number} бесплатных блока"
    else:
        return f"{number} бесплатных блоков"


async def user_start(message: Message):
    if Db().user_exist(message.from_user.id) is False:
        Db().add_user(message)
        balance = Db().get_user(message.from_user.id).balance
        msg = Db().get_message('msg_start').Message.replace('[balance_free_block]', sklonenie_blocks(int(balance)))
        await message.answer(text=msg, reply_markup=InlineKeyboard().menu())
    else:
        msg = Db().get_message('msg_start_old').Message
        await message.answer(text=msg, reply_markup=InlineKeyboard().menu())


