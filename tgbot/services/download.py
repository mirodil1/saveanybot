from tgbot.config import load_config
from tgbot.services.db import db
from datetime import datetime
import youtube_dl
import requests
from datetime import datetime
import time
config = load_config(".env")


async def download_from_youtube(video_url):
    url = "https://fastest-social-video-and-image-downloader.p.rapidapi.com/youtube"

    querystring = {"url": video_url}

    headers = {
        "X-RapidAPI-Key": config.misc.rapid_api_key_pinterest,
        "X-RapidAPI-Host": "fastest-social-video-and-image-downloader.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        if response['success']:
            await db.add_api_request(name='youtube-fastest-api',
                                    status=True,
                                    created_at=datetime.now())
            try:
                result = {
                    'hasError': False,
                    'thumb': response['thumbnail'],
                    'items': [
                        {
                            'url': response['data']['360p'],
                            'quality': '360',
                            'type': 'mp4' 
                        },
                        {
                            'url': response['data']['720p'],
                            'quality': '720',
                            'type': 'mp4' 
                        }
                    ]
                }
            except:
                result = {
                    'hasError': False,
                    'thumb': response['thumbnail'],
                    'items': [
                        {
                            'url': response['data']['360p'],
                            'quality': '360',
                            'type': 'mp4' 
                        },
                    ]
                }
        elif not response['success']:
            await db.add_api_request(name='youtube-fastest-api',
                                    status=False,
                                    created_at=datetime.now())
            result = {
                'hasError': True,
            }
        return result
    except:
        await db.add_api_request(name='youtube-fastest-api',
                                status=False,
                                created_at=datetime.now())
        result = {
            'hasError': True,
        }
        return result


async def download_from_pinterest(link):

    url = "https://fastest-social-video-and-image-downloader.p.rapidapi.com/pinterest"

    querystring = {"url":link}

    headers = {
        "X-RapidAPI-Key": config.misc.rapid_api_key_pinterest,
        "X-RapidAPI-Host": "fastest-social-video-and-image-downloader.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if response['success']:
        return response
    elif not response['success']:
        return response


async def download_from_likee(video_url):
    ydl_opts = {
        'outtmpl': 'media/%(title)s.%(ext)s',
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            uri = video_url
            info = ydl.extract_info(uri, download=True)
            filename = ydl.prepare_filename(info)

        return {"hasError": False, "url":filename}
    except:
        return {"hasError": True}


async def all_in_one(link):
    url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

    payload = {"url": link}

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.misc.rapid_api_key,
        "X-RapidAPI-Host": "auto-download-all-in-one.p.rapidapi.com"
    }
    try:
        response = requests.post(url, json=payload, headers=headers).json()
    except:
        response = {"error": True}
    return response
