from tgbot.config import load_config
from tgbot.services.db import db
from datetime import datetime
import youtube_dl
import requests

config = load_config(".env")

async def download_from_facebook(video_url):

    url = "https://socialdownloader.p.rapidapi.com/api/facebook/video"
    
    headers = {
	"X-RapidAPI-Host": "socialdownloader.p.rapidapi.com",
	"X-RapidAPI-Key": config.misc.rapid_api_key
    }

    querystring = {"video_link":video_url}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if not response['hasError']:
        await db.add_api_request(name='facebook',
                                 status=True,
                                 created_at=datetime.now())
    elif response['hasError']:
        await db.add_api_request(name='facebook',
                                 status=False,
                                 created_at=datetime.now())
    return response

async def download_from_instagram(link):

    url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"

    querystring = {"url":link}

    headers = {
        "X-RapidAPI-Key": config.misc.rapid_api_key,
        "X-RapidAPI-Host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if 'error' not in response:
        await db.add_api_request(name='instagram',
                                 status=True,
                                 created_at=datetime.now())
        return response
    else:
        await db.add_api_request(name='instagram',
                                 status=False,
                                 created_at=datetime.now())
        return response

async def download_video_from_tiktok(video_url):
    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"

    querystring = {"url":video_url}

    headers = {
        "X-RapidAPI-Key": config.misc.rapid_api_key,
        "X-RapidAPI-Host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if 'Roung URL' not in response:
        await db.add_api_request(name='tiktok',
                                 status=True,
                                 created_at=datetime.now())
    else:
        await db.add_api_request(name='tiktok',
                                 status=False,
                                 created_at=datetime.now())
    return response

async def download_from_youtube(video_url):
    items = list()
    url = "https://socialdownloader.p.rapidapi.com/api/youtube/video"
    
    headers = {
	"X-RapidAPI-Host": "socialdownloader.p.rapidapi.com",
	"X-RapidAPI-Key": config.misc.rapid_api_key
    }

    querystring = {"video_link":video_url}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if not response['hasError']:
        res = response['body']['url']
        await db.add_api_request(name='youtube',
                                 status=True,
                                 created_at=datetime.now())
        for item in res:
            try:
                if ((item['type'] == "mp4 dash" or item['type'] == "mp4") and  (item['no_audio'] == False and (item['quality']=='360' or item['quality']=='720'))):
                    items.append(item)
            except Exception as e:
                print(e)
        return {'hasError': response['hasError'], 'thumb': response['body']['thumb'], 'items': items}
    elif response['hasError']:
        await db.add_api_request(name='youtube',
                                 status=False,
                                 created_at=datetime.now())
        return {"hasError": True}

async def download_from_vkontakte(video_url):

    url = "https://socialdownloader.p.rapidapi.com/api/vkontakte/video"
    
    headers = {
	"X-RapidAPI-Host": "socialdownloader.p.rapidapi.com",
	"X-RapidAPI-Key": config.misc.rapid_api_key
    }
    querystring = {"video_link":video_url}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if not response['hasError']:
        items = response['body']['videos']
        await db.add_api_request(name='vkontakte',
                                 status=True,
                                 created_at=datetime.now())
        return {'hasError': response['hasError'], 'videos': {items}}
    elif response['hasError']:
        await db.add_api_request(name='vkontakte',
                                 status=False,
                                 created_at=datetime.now())
        return {"hasError": response['hasError']}

async def download_from_twitter(video_url):

    # url = "https://socialdownloader.p.rapidapi.com/api/twitter/video"
    
    # headers = {
	# "X-RapidAPI-Host": "socialdownloader.p.rapidapi.com",
	# "X-RapidAPI-Key": config.misc.rapid_api_key
    # }

    # querystring = {"video_link":video_url}
    # response = requests.request("GET", url, headers=headers, params=querystring).json()
    # if not response['hasError']:
    #     await db.add_api_request(name='twitter',
    #                              status=True,
    #                              created_at=datetime.now())
    #     return {'hasError': response['hasError'], 'url': response['body']['url']}
    # elif response['hasError']:
    #     await db.add_api_request(name='twitter',
    #                              status=False,
    #                              created_at=datetime.now())
    #     return {'hasError': response['hasError']}

    ydl_opts = {
        'outtmpl': 'tgbot/media/%(title)s.%(ext)s',
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            uri = video_url
            info = ydl.extract_info(uri, download=True)
            filename = ydl.prepare_filename(info)
        await db.add_api_request(name='twitter',
                                 status=True,
                                 created_at=datetime.now())
        return {"hasError": False, "url":filename}
    except Exception as e:
        print(e)
        await db.add_api_request(name='twitter',
                                 status=False,
                                 created_at=datetime.now())
        return {"hasError": True}


async def download_from_pinterest(link):

    url = "https://fastest-social-video-and-image-downloader.p.rapidapi.com/pinterest"

    querystring = {"url":link}

    headers = {
        "X-RapidAPI-Key": config.misc.rapid_api_key_pinterest,
        "X-RapidAPI-Host": "fastest-social-video-and-image-downloader.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if response['success']:
        await db.add_api_request(name='pinterest',
                                 status=True,
                                 created_at=datetime.now())
        return response
    elif not response['success']:
        await db.add_api_request(name='pinterest',
                                 status=False,
                                 created_at=datetime.now())
        return response