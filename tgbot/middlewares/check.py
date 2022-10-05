from datetime import datetime
import logging
from typing import Any, Tuple, List, Dict, Optional
from unittest import result
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.services.db import db
from tgbot.services.check_sub import check_user_sub
from tgbot.keyboards.inline import subscription_button
# from tgbot.middlewares.i18n import _
import asyncpg
import re

from tgbot.middlewares.i18n import CustomI18nMiddleware
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOCALES_DIR ='locales'

_ = i18n = CustomI18nMiddleware("savebot", LOCALES_DIR)

class CheckSubscriptionMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        URL_REGEX = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'.,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"
        final_status = True
        result = None
        sub_msg = "Please, subscribe to the following channels to use bot."
        credits_msg = "Your limit for today is over."

        channels_record = await db.select_all_channels()
        channels = list(dict(channel) for channel in channels_record)
        
        if update.callback_query:
            user_id = update.callback_query.from_user.id

            # saving user to DB
            try:
                user = await db.add_user(
                    telegram_id = update.callback_query.from_user.id,
                    full_name = update.callback_query.from_user.full_name,
                    username = update.callback_query.from_user.username,
                    language_code = update.callback_query.from_user.language_code,
                    credits = 10,
                    is_premium=False,
                    joined_date = datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                user = await db.select_user(telegram_id=update.callback_query.from_user.id)

            if update.callback_query.data == "check_subs":
                for channel in channels:
                    status = await check_user_sub(user_id=user_id, channel=channel['username'])
                    final_status *= status
                if final_status:
                    await update.callback_query.message.edit_text(_("<b>Send a link and get your media!</b>\n\nYou can download photo and video files from popular social media!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"))
                else:
                    await update.callback_query.answer(_("Please, subscribe to the following channels to use bot."), show_alert=True)
        elif update.message:

            # saving user to DB
            try:
                user = await db.add_user(
                    telegram_id = update.message.from_user.id,
                    full_name = update.message.from_user.full_name,
                    username = update.message.from_user.username,
                    language_code = update.message.from_user.language_code,
                    credits = 10,
                    is_premium=False,
                    joined_date = datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                user = await db.select_user(telegram_id=update.message.from_user.id)
            
            try:
                result = re.match(URL_REGEX, update.message.text)
            except:
                pass
            user_id = update.message.from_user.id
        else:
            return

        credits = dict(await db.get_credits(user_id))

        # get channels buy user language
        channels = [channel for channel in channels if user['language_code'] in channel['language'].split(',')]
        
        for channel in channels:
            if channel['status']:
                status = await check_user_sub(user_id=user_id, channel=channel['username'])
                final_status *= status
        if result:
            if not final_status:
                try:
                    await update.message.answer(_("Please, subscribe to the following channels to use bot."), disable_web_page_preview=True, reply_markup=await subscription_button(channels, user_id))
                    raise CancelHandler()
                except:
                    raise CancelHandler()
            if credits['credits'] <= 0:
                try:
                    await update.message.answer(_("Your limit for today is over."))
                    raise CancelHandler()
                except:
                    raise CancelHandler()