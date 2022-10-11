from cmath import inf
from dataclasses import dataclass
from datetime import datetime
from aiogram import Dispatcher
from aiogram import types
from aiogram.types import Message
from aiogram.types import InputFile
from tgbot.middlewares.i18n import _
import asyncpg

from tgbot.keyboards.inline import lang_button, response_callback_lang
from tgbot.services.db import db
from aiogram.utils.deep_linking import get_start_link

from pathlib import Path

import youtube_dl
async def user_start(message: Message):
    args = message.get_args()
    if args:
        await db.add_invite_link(
            name=args,
            created_at=datetime.now()
        )
    await message.answer(_("<b>Send a link and get your media!</b>\n\nYou can download photo and video files from popular social media!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"))
    
async def lang_command(message: Message):
    await message.answer(_("Choose language"), reply_markup=lang_button)

async def change_langueage(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    lang_code = callback_data.get('code')
    await db.set_language_code(language_code=lang_code, telegram_id=user_id)
    await call.message.edit_text(_("Language changed"))
    await call.answer(cache_time=10)

def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(lang_command, commands=["lang"])
    dp.register_callback_query_handler(change_langueage, response_callback_lang.filter())