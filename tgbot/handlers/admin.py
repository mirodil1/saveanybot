from aiogram import Dispatcher, Bot
from aiogram import types
from aiogram.dispatcher import filters, FSMContext
from aiogram.utils.deep_linking import get_start_link
from tgbot.keyboards.inline import  response_callback, send_msg_button, response_callback_confirm
from tgbot.misc.states import Message, Link
from tgbot.services.db import db
import asyncio

from tgbot.config import load_config

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
async def admin_start(message: Message):
    await message.reply("Hello, admin!")


async def command_link(message: Message):
    await message.answer("Link uchun so'zni kiriting.\nA-Z, a-z, 0-9, _ va - ruxsat etiladi.")
    await Link.link.set()
    
async def get_deep_link(message: types.Message, state: FSMContext):
    link = await get_start_link(message.text)
    await message.answer(link)
    await state.finish()


async def ads(message: types.Message):
        await message.answer("Istagan xabaringizni kiriting")
        await Message.message.set()

async def prepare_to_send(message: types.Message, state: FSMContext):
    counter = await db.count_users_by_language()
    await bot.copy_message(from_chat_id=message.from_user.id, chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(f"Xabar {counter} foydalanuchiga yuboriladi", reply_markup=send_msg_button)
    async with state.proxy() as data:
        data['message'] = message.message_id
        data['from_user_id'] = message.from_user.id

async def confirmation(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    call_data = callback_data['confirm']
    count = 0
    if call_data == 'agree':
        data = await state.get_data()
        from_user_id = data.get('from_user_id')
        message_id = data.get('message')
        users = await db.select_all_uz_users()
        await call.message.edit_text("Xabar yuborilyapti")
        await state.finish()
        for user in users:
            user = dict(user)
            try:
                await bot.copy_message(from_chat_id=from_user_id, chat_id=user['telegram_id'], message_id=message_id)
                count+=1
            except:
                print(f"Bot was blocked by {user}")
            await asyncio.sleep(0.05)
        await call.message.answer(f"Xabar {count} ta foydalanuvchiga yuborildi.")
    elif call_data == 'disagree':
        await call.message.delete()
        await call.message.answer("Bekor qilindi.")
        await call.answer(cache_time=15)
        await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)

    dp.register_message_handler(ads, commands=["reklama"], is_admin=True)
    dp.register_message_handler(prepare_to_send, content_types=[types.ContentType.ANY], state=Message.message, is_admin=True)
    dp.register_callback_query_handler(confirmation, response_callback_confirm.filter(), state=Message.message, is_admin=True)

    dp.register_message_handler(command_link, commands=["link"], is_admin=True)
    dp. register_message_handler(get_deep_link, state=Link.link, is_admin=True)