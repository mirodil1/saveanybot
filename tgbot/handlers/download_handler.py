import os
from datetime import datetime

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import filters

from tgbot.services.download import download_from_pinterest, download_from_likee, all_in_one
from tgbot.middlewares.i18n import _
from tgbot.services.db import db
from tgbot.keyboards.inline import download_button, download_youtube_button


YOUTUBE_REGEX = r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'
INSTA_REGEX = r'((?:https?:\/\/www\.)?instagram\.com\/)'
TWITTER_REGEX = r'((?:https?:\/\/www\.)?(?:twitter\.com\/|x\.com\/))'
VKONTAKTE_REGEX = r'((?:https?:\/\/www\.)?vk\.com\/)'
TIKTOK_REGEX = r'((?:https?:\/\/)?(?:www|m\.)?tiktok\.com\/)'
FACEBOOK_REGEX = r'(?:https?:\/\/)?(?:www\.|web\.|m\.)?fb|facebook\.com\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'
PINTEREST_REGEX = r'^https?://(?:www\.)?pinterest\.com/|https?://pin\.it/.*$'
LIKEE_REGEX = r'(?:http[s]?:\/\/)?(?:www\.)?(?:likee\.com\/|likee\.video\/|like\.video\/|video\.likee\.co\/|video\.like\.co\/|video\.likee\.video\/|like\.ly\/)'


async def youtube_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    link = message.text
    result = await all_in_one(link)
    if not result["error"]:
        await waiting_msg.delete()
        for media in result['medias']:
            if media['type'] == 'video' and media['quality'] == '360p':
                try:
                    await message.answer_video(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                except Exception as e:
                    await message.answer(
                        _("Size of media is too large but you can download it from link"),
                        reply_markup=await download_button(media['url'])
                    )
            elif media['type'] == 'audio':
                try:
                    await message.answer_audio(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                except Exception as e:
                    pass # do nothing
        await db.consume_credits(telegram_id=message.from_user.id)
        await db.add_api_request(name='youtube', status=True, created_at=datetime.now())
    else:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

        # Record status of result
        await db.add_api_request(name='youtube', status=False, created_at=datetime.now())


async def youtube_callback_handler(callback: types.CallbackQuery, callback_data: dict):
    url = callback_data.split(":")[0]
    content_type = callback_data.split(":")[1]

    try:
        if content_type == "audio":
            await callback.message.answer_audio(url, caption=_("@SaveAnyBot — Save Any Media!"))
            await db.consume_credits(telegram_id=message.from_user.id)
            await db.add_api_request(name='youtube', status=True, created_at=datetime.now())
        elif content_type == "video":
            await callback.message.answer_video(url, caption=_("@SaveAnyBot — Save Any Media!"))
            await db.consume_credits(telegram_id=message.from_user.id)
            await db.add_api_request(name='youtube', status=True, created_at=datetime.now())
        else:
            await message.answer(
                _("Something went wrong, try again."),
            )
    except:
        await message.answer(_("Something went wrong, try again."))


async def twitter_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    link = message.text
    result = await all_in_one(link)
    if not result["error"]:
        await waiting_msg.delete()
        try:
            media = result["medias"][0]
            if media["type"] == "photo":
                await message.answer_photo(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
            elif media["type"] == "video":
                try:
                    await message.answer_video(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                except Exception as e:
                    await message.answer(
                        _("Size of media is too large but you can download it from link"),
                        reply_markup=await download_button(media['url'])
                    )
            # Update user credits
            await db.consume_credits(telegram_id=message.from_user.id)

            # Record status of result
            await db.add_api_request(name='twitter', status=True, created_at=datetime.now())
        except:
            await message.answer(_("Something went wrong, try again."))

    elif result["error"]:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

        # Record status of result
        await db.add_api_request(name='twitter', status=False, created_at=datetime.now())


async def insta_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    link = message.text
    result = await all_in_one(link)
    if not result["error"]:
        await waiting_msg.delete()
        try:
            if result["type"] == "single":
                media = result["medias"][0]
                if media["type"] == "image":
                    await message.answer_photo(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                elif media["type"] == "video":
                    try:
                        await message.answer_video(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                    except Exception as e:
                        print(e)
                        await message.answer(
                            _("Size of media is too large but you can download it from link"),
                            reply_markup=await download_button(media['url'])
                        )
            elif result["type"] == "multiple":
                for media in result["medias"]:
                    if media["type"] == "image":
                        await message.answer_photo(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                    elif media["type"] == "video":
                        try:
                            await message.answer_video(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                        except Exception as e:
                            print(e)
                            await message.answer(
                                _("Size of media is too large but you can download it from link"),
                                reply_markup=await download_button(media['url'])
                            )
            # Update user credits
            await db.consume_credits(telegram_id=message.from_user.id)
            
            # Record status of result
            await db.add_api_request(name='instagram', status=True, created_at=datetime.now())
        except:
            await message.answer(_("Something went wrong, try again."))
    else:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

        # Record status of result
        await db.add_api_request(name='instagram', status=False, created_at=datetime.now())


async def tiktok_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await all_in_one(video_url)
    if not result["error"]:
        await waiting_msg.delete()
        try:
            for media in result["medias"]:
                if media["type"] == "video":
                    if media["quality"] == "no_watermark":
                        try:
                            await message.answer_video(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                        except Exception as e:
                            await message.answer(
                                _("Size of media is too large but you can download it from link"),
                                reply_markup=await download_button(media['url'])
                            )
                if media["type"] == "audio":
                    await message.answer_audio(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                if media["type"] == "image":
                    try:
                        await message.answer_photo(media['url'], caption=_("@SaveAnyBot — Save Any Media!"))
                    except:
                        await message.answer(
                            _("Size of media is too large but you can download it from link"),
                            reply_markup=await download_button(media['url'])
                        )

            # Update user credits
            await db.consume_credits(telegram_id=message.from_user.id)
            
            # Record status of result
            await db.add_api_request(name='tiktok', status=True, created_at=datetime.now())
        except Exception as e:
            await message.answer(_("Something went wrong, try again."))
    else:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

        # Record status of result
        await db.add_api_request(name='tiktok', status=False, created_at=datetime.now())


async def facebook_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    link = message.text
    result = await all_in_one(link)
    if not result["error"]:
        await waiting_msg.delete()
        try:
            for media in result["medias"]:
                if media["type"] == "video" and media["quality"] == "sd":
                    try:
                        await message.answer_video(media["url"], caption=_("@SaveAnyBot — Save Any Media!"))
                    except Exception:
                        await message.answer(
                            _("Size of media is too large but you can download it from link"),
                            reply_markup=await download_button(media["url"])
                        )
        except:
            await message.answer(_("Something went wrong, try again."))

        # Update user credits
        await db.consume_credits(telegram_id=message.from_user.id)

        # Record status of result
        await db.add_api_request(name='facebook', status=True, created_at=datetime.now())

    else:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))
        
        # Record status of result
        await db.add_api_request(name='facebook', status=False, created_at=datetime.now())


async def pinterest_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await download_from_pinterest(video_url)
    if result['success']:
        await waiting_msg.delete()
        if result['type'] == 'video':
            try:
                await message.answer_video(result['data']['url'], caption=_("@SaveAnyBot — Save Any Media!"))
            except:
                await message.answer(
                    _("Size of media is too large but you can download it from link"),
                    reply_markup=await download_button(result['data']['url'])
                )
        
        elif result['type'] == 'image':
            try:
                await message.answer_photo(result['data']['url'], caption=_("@SaveAnyBot — Save Any Media!"))
            except:
                await message.answer(_("Something went wrong, try again."))

        # Update user credits
        await db.consume_credits(telegram_id=message.from_user.id)

        # Record status of result
        await db.add_api_request(name='pinterest', status=True, created_at=datetime.now())
    elif not result['success']:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

        # Record status of result
        await db.add_api_request(name='pinterest', status=False, created_at=datetime.now())


async def likee_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await download_from_likee(video_url)
    if not result["hasError"]:
        await waiting_msg.delete()
        try:
            file_path = types.InputFile(path_or_bytesio=result['url'])
            await message.answer_video(file_path, caption=_("@SaveAnyBot — Save Any Media!"))
            os.remove(result['url'])

            # Update user credits
            await db.consume_credits(telegram_id=message.from_user.id)

            # Record status of result
            await db.add_api_request(name='likee', status=True, created_at=datetime.now())
        except:
            await message.answer(_("Something went wrong, try again."))
    elif result["hasError"]:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

        # Record status of result
        await db.add_api_request(name='likee', status=False, created_at=datetime.now())


def register_download_handler(dp: Dispatcher):
    dp.register_message_handler(likee_download_handler, filters.Regexp(LIKEE_REGEX))
    dp.register_message_handler(insta_download_handler, filters.Regexp(INSTA_REGEX))    
    dp.register_message_handler(youtube_download_handler, filters.Regexp(YOUTUBE_REGEX))
    dp.callback_query_handler()
    dp.register_message_handler(twitter_download_handler, filters.Regexp(TWITTER_REGEX))
    dp.register_message_handler(tiktok_download_handler, filters.Regexp(TIKTOK_REGEX))
    dp.register_message_handler(facebook_download_handler, filters.Regexp(FACEBOOK_REGEX))
    dp.register_message_handler(pinterest_download_handler, filters.Regexp(PINTEREST_REGEX))
