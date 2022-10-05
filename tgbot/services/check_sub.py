from typing import Union
from aiogram import Bot

async def check_user_sub(user_id, channel: Union[int, str]):
    bot = Bot.get_current()
    try:
        member = await bot.get_chat_member(user_id=user_id, chat_id=channel)
        return member.is_chat_member()
    except:
        return True