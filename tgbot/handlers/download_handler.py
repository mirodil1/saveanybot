from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import filters

from tgbot.services.download import download_from_twitter, download_from_youtube, download_from_instagram, \
                                    download_video_from_tiktok, download_from_facebook, download_from_vkontakte, \
                                    download_from_pinterest, download_from_instagram_by_username
from tgbot.services.other import url_shortener
from tgbot.middlewares.i18n import _
from tgbot.services.db import db
from tgbot.keyboards.inline import download_button, download_youtube_button

import os

YOUTUBE_REGEX = r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'
INSTA_REGEX = r'((?:https?:\/\/www\.)?instagram\.com\/)'
TWITTER_REGEX = r'((?:https?:\/\/www\.)?twitter\.com\/)'
VKONTAKTE_REGEX = r'((?:https?:\/\/www\.)?vkontakte\.com\/)'
TIKTOK_REGEX = r'((?:https?:\/\/)?(?:www|m\.)?tiktok\.com\/)'
FACEBOOK_REGEX = r'(?:https?:\/\/)?(?:www\.|web\.|m\.)?facebook\.com\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'
PINTEREST_REGEX = r'((?:https?:\/\/www\.)?pinterest\.com\/)'
INSTA_USERNAME_REGEX = r'^[a-zA-Z0-9_.@]+$'


async def youtube_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await download_from_youtube(video_url)
    if not result['hasError']:
        await waiting_msg.delete()
        try:
            await message.answer_photo(result['thumb'], caption=_("@SaveAnyBot — Save Any Media!"))
        except Exception as e:
            print(e)
        try:
            for item in result['items']:
                await message.answer_video(item['url'], caption=_("@SaveAnyBot — Save Any Media!"))
        except:
            try:
                await message.answer(_("Size of media is too large but you can download it from link"), reply_markup=await download_youtube_button(result['items']))
            except:
                await message.answer(_("Something went wrong, try again."))
        await db.consume_credits(telegram_id=message.from_user.id)
    elif result['hasError']:
        await message.answer(_("Something went wrong, try again."))

async def twitter_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await download_from_twitter(video_url)
    if not result['hasError']:
        await waiting_msg.delete()
        try:
            file_path = types.InputFile(path_or_bytesio=result['url'])
            await message.answer_video(file_path, caption=_("@SaveAnyBot — Save Any Media!"))
            os.remove(result['url'])
        except:
            await message.answer(_("Size of media is too large but you can download it from link"), reply_markup=await download_button(result['url']))
        await db.consume_credits(telegram_id=message.from_user.id)
    elif result['hasError']:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

async def insta_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    link = message.text
    result = await download_from_instagram(link)
    try:
        await waiting_msg.delete()
        if isinstance(result, list):
            result = result[0]
            if result['type'] == 'Video':
                await message.answer_video(result['media'], caption=_("@SaveAnyBot — Save Any Media!"))
            elif result['type'] == 'Image':
                await message.answer_photo(result['media'], caption=_("@SaveAnyBot — Save Any Media!"))
        elif isinstance(result, dict):
            if result['Type'] == 'Story-Video':
                await message.answer_video(result['media'][0], caption=_("@SaveAnyBot — Save Any Media!"))
            elif result['Type'] == 'Story-Image':
                await message.answer_photo(result['media'][0], caption=_("@SaveAnyBot — Save Any Media!"))
        elif result['Type'] == 'Post-Video':
            try:
                await message.answer_video(result['media'], caption=_("@SaveAnyBot — Save Any Media!"))
            except Exception as e:
                await message.answer(_("Size of media is too large but you can download it from link"), reply_markup=await download_button(result['media']))
                print(e)
        elif result['Type'] == 'Post-Image':
            await message.answer_photo(result['media'], caption=_("@SaveAnyBot — Save Any Media!"))
        elif result['Type'] == 'Carousel':
            for m in result['media']:
                await message.answer_video(m, caption=_("@SaveAnyBot — Save Any Media!"))
        await db.consume_credits(telegram_id=message.from_user.id)
    except:
        await message.answer(_("Something went wrong, try again."))

async def tiktok_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    try:
        result = await download_video_from_tiktok(video_url)
        await waiting_msg.delete()
        await message.answer_video(result['video'][0], caption=_("@SaveAnyBot — Save Any Media!"))
        await message.answer_audio(result['music'][0], caption=_("@SaveAnyBot — Save Any Media!"))
        await db.consume_credits(telegram_id=message.from_user.id)
    except:
        await message.answer(_("Something went wrong, try again."))

async def facebook_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await download_from_facebook(video_url)
    if not result['hasError']:
        try:
            await waiting_msg.delete()
            await message.answer_video(result['body']['video'], caption=_("@SaveAnyBot — Save Any Media!"))
        except Exception as e:
            print(e)
            try:
                await message.answer(_("Size of media is too large but you can download it from link"), reply_markup=await download_button(result['body']['video']))
            except:
                pass
                # await message.answer("Something went wrong, try again.")
        await db.consume_credits(telegram_id=message.from_user.id)
    elif result['hasError']:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

async def vk_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    video_url = message.text
    result = await download_from_vkontakte(video_url)
    if not result['hasError']:
        await waiting_msg.delete()
        for video in result['videos']:
            try:
                await message.answer_video(video['url'], caption=_("@SaveAnyBot — Save Any Media!"))
            except:
                await message.answer(_("Size of media is too large but you can download it from link"), reply_markup=await download_button(video['url']))
        await db.consume_credits(telegram_id=message.from_user.id)
    elif result['hasError']:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

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
                await message.answer(_("Size of media is too large but you can download it from link"), reply_markup=await download_button(result['data']['url']))
        
        elif result['type'] == 'image':
            try:
                await message.answer_photo(result['data']['url'], caption=_("@SaveAnyBot — Save Any Media!"))
            except Exception as e:
                print(e)
        await db.consume_credits(telegram_id=message.from_user.id)

    elif not result['success']:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))

async def insta_by_username_download_handler(message: types.Message):
    waiting_msg = await message.answer('🔍')
    username = message.text
    if not username.startswith("@"):
        username = "@"+username

    result = await download_from_instagram_by_username(username)
    if not result['hasError']:
        
        album_video = types.MediaGroup()
        album_img = types.MediaGroup()

        videos = result['video_story']
        images = result['image_story']

        if len(videos) > 0 or len(images) > 0:
            # adding url list to album
            for video in videos:
                album_video.attach_video(video, caption=_("@SaveAnyBot — Save Any Media!"))
            for image in images:
                album_img.attach_photo(image, caption=_("@SaveAnyBot — Save Any Media!"))

            await waiting_msg.delete()

            # sending video album
            try:
                await message.answer_media_group(media=album_video)
            except Exception as e:
                try:
                    for video in videos:
                        await message.answer_video(video, caption=_("@SaveAnyBot — Save Any Media!"))
                except Exception as e:
                    print(e)
                    await message.answer(_("Something went wrong, try again."))
            
            # sending photo album
            try:
                await message.answer_media_group(media=album_img)
            except Exception as e:
                try:
                    for image in images:
                        await message.answer_photo(image, caption=_("@SaveAnyBot — Save Any Media!"))
                except Exception as e:
                    print(e)
                    await message.answer(_("Something went wrong, try again."))
        else:
            await waiting_msg.delete()
            await message.answer(_("Story not found"))

        await db.consume_credits(telegram_id=message.from_user.id)


    elif result['hasError']:
        await waiting_msg.delete()
        await message.answer(_("Something went wrong, try again."))


def register_download_handler(dp: Dispatcher):
    dp.register_message_handler(insta_download_handler, filters.Regexp(INSTA_REGEX))    
    dp.register_message_handler(youtube_download_handler, filters.Regexp(YOUTUBE_REGEX))
    dp.register_message_handler(twitter_download_handler, filters.Regexp(TWITTER_REGEX))
    dp.register_message_handler(tiktok_download_handler, filters.Regexp(TIKTOK_REGEX))
    dp.register_message_handler(facebook_download_handler, filters.Regexp(FACEBOOK_REGEX))
    dp.register_message_handler(vk_download_handler, filters.Regexp(VKONTAKTE_REGEX))
    dp.register_message_handler(pinterest_download_handler, filters.Regexp(PINTEREST_REGEX))
    dp.register_message_handler(insta_by_username_download_handler, filters.Regexp(INSTA_USERNAME_REGEX))