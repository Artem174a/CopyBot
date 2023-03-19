import urllib.request
import bs4
import requests
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from tgbot.database.DB import Database as Db
from tgbot.keyboards.inline import *
from aiocryptopay import AioCryptoPay, Networks


def sklonenie_blocks(number):
    if number % 10 == 1 and number % 100 != 11:
        return f"<code>{number}</code> блок"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return f"<code>{number}</code> блока"
    else:
        return f"<code>{number}</code> блоков"


def parser(url):
    try:
        fp = urllib.request.urlopen(url)
        mybytes = fp.read()
        html_content = mybytes.decode("utf8")
        fp.close()
        soup = bs4.BeautifulSoup(html_content, 'html.parser')
        point = soup.find('div', {'id': 'allrecords'}).findAll(attrs={"data-record-type": "396"})

        ids = []
        for elem in point:
            ids.append(elem["id"])
        return ids
    except:
        return []


def convert(price):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB"
    data = requests.get(key)
    data = data.json()
    return price / float(data['price'])


async def user_call_registered(call: CallbackQuery, state: FSMContext):
    if 'get_block' in call.data:
        await eval(f'get_block(call=call, state=state)')
    if 'pay' in call.data:
        await eval(f'pay(call=call, state=state)')
    else:
        await eval(f'{call.data}(call=call, state=state)')


async def menu(call: CallbackQuery, state: FSMContext):
    if await state.get_state() == 'get_site':
        await state.finish()
    msg = '''
<b>Меню</b>
<em>Нажмите на кнопку чтобы выбрать</em>
'''
    await call.message.edit_text(text=msg, reply_markup=InlineKeyboard().menu())


async def get_balance(call: CallbackQuery, state: FSMContext):
    balance = Db().get_user(call.from_user.id).balance
    msg = f'''
<b>Меню</b>
<em>Нажмите на кнопку чтобы выбрать</em>

<b>У вас: {sklonenie_blocks(balance)}</b>
'''
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton
    buttons = [
        button(text='Купить', callback_data='buy'),
        button(text='Скопировать блок', callback_data='copy_block'),
        button(text='Инструкция', callback_data='info'),
        button(text='Назад', callback_data='menu')
    ]
    keyboard.row(buttons[0], buttons[1])
    keyboard.row(buttons[2])
    keyboard.row(buttons[3])
    await call.message.edit_text(text=msg, reply_markup=keyboard)


async def buy(call: CallbackQuery, state: FSMContext):
    balance = Db().get_user(call.from_user.id).balance
    products = Db().up_product()
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []
    button = InlineKeyboardButton
    msg = f'''
<b>Цены</b>
<em>Нажмите на кнопку чтобы выбрать</em>

<b>У вас: {sklonenie_blocks(balance)}</b>
    '''
    for product in products:
        buttons.append(button(text=str(product[0]), callback_data=f'pay_{product[0]}'))
    keyboard.add(*buttons)
    keyboard.add(button(text='Назад', callback_data='menu'))
    await call.message.edit_text(text=msg, reply_markup=keyboard)


async def pay(call: CallbackQuery, state: CallbackQuery):
    title = call.data[4:]
    product = Db().get_product(title=title)
    balance = Db().get_user(call.from_user.id).balance
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton
    msg = f'''
<b>Оплата</b>
<em>Нажмите на кнопку чтобы оплатить</em>

<b>У вас: {sklonenie_blocks(balance)}</b>

=======================
<b>Оплата:</b>

<b>Название: {product.Title}</b>
<b>Цена: {product.Price}₽</b> 
=======================
'''
    price = convert(int(product.Price))
    '''Генерируем ссылку на оплату'''
    crypto = AioCryptoPay(token='91360:AAjByohA2vL3esTAUXk7nP9HStEnBqF548p', network=Networks.MAIN_NET)
    invoice = await crypto.create_invoice(asset='BTC', amount=price)
    invoices = await crypto.get_invoices(invoice_ids=invoice.invoice_id)
    '''Генерируем ссылку на оплату'''

    keyboard.add(button(text=f'Оплатить {product.Price}₽', url=invoice.pay_url))
    keyboard.add(button(text="Назад", callback_data='menu'))
    await call.message.edit_text(text=msg, reply_markup=keyboard)


async def copy_block(call: CallbackQuery, state: FSMContext):
    msg = '''
<b>Скопировать блок</b>

Введите ссылку на сайт:
'''
    await call.message.edit_text(text=msg)
    await state.set_state(state='get_site')


async def get_site(message: Message, state: FSMContext):
    url = message.text
    blocks = parser(url)
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []
    button = InlineKeyboardButton
    msg = f'''
<b>Скопировать блок</b>

<b>Сайт: </b><em>{message.text}</em>
'''
    if blocks:
        for block in blocks:
            buttons.append(button(text=block, callback_data='get_block_{}'.format(block)))
        keyboard.add(*buttons)
        keyboard.add(button(text=f'Скопировать все {len(blocks)}', callback_data='get_block_all'.format()))
        keyboard.add(button(text="Назад", callback_data='menu'))
        msg += f'\n<b>Найдено: {sklonenie_blocks(len(blocks))}</b>\n<em>Нажмите на нужный Zero-block и получите код для вставки</em>'
    else:
        msg += '\n<b>Блоки не найдены\nВведите ссылку на сайт:</b>'
        keyboard.add(button(text="Назад", callback_data='menu'))
    await message.answer(text=msg, reply_markup=keyboard, disable_web_page_preview=True)


async def get_block(call: CallbackQuery, state: FSMContext):
    await call.answer(text='Недоступно', show_alert=True)


async def info(call: CallbackQuery, state: FSMContext):
    msg = Db().get_message('msg_help').Message
    keyboard = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton
    buttons = [
        button(text='Как узнать ID блока?', callback_data='how_id'),
        button(text="Назад", callback_data='menu')
    ]
    keyboard.add(*buttons)
    await call.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True)


async def how_id(call: CallbackQuery, state: FSMContext):
    msg = Db().get_message('msg_how_id').Message
    keyboard = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton
    buttons = [
        button(text="Назад", callback_data='menu')
    ]
    keyboard.add(*buttons)
    await call.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True)