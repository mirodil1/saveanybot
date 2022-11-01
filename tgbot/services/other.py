from tgbot.config import load_config
import requests

config = load_config(".env")

async def url_shortener(link):
    url = "https://url-shortener20.p.rapidapi.com/shorten"

    querystring = {"url":link}

    payload = {"url": "https://www.bbc.com/sport/football"}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.misc.rapid_api_key,
        "X-RapidAPI-Host": "url-shortener20.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring).json()
    return response['short_link']