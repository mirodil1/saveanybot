from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.middlewares.i18n import _
from tgbot.services.check_sub import check_user_sub

from tgbot.config import load_config

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')


# Subscription button
response_callback = CallbackData("channel", "link")

async def subscription_button(channels, user):

    markup = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        if ch['status']:
            status = await check_user_sub(user_id=user, channel=ch['username'])
        try:
            channel = await bot.get_chat(ch['username'])
        except:
            pass
        if not status:
            markup.insert(
                InlineKeyboardButton(text="{title}".format(title=channel.title), url= ch['invite_link'])
            )
    markup.insert(
        InlineKeyboardButton(_("✅ Subscribed"), callback_data="check_subs")
    )
    return markup


# admin button
response_callback_confirm = CallbackData('confirmation', 'confirm')

send_msg_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlayman", callback_data=response_callback_confirm.new(confirm="agree")),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=response_callback_confirm.new(confirm="disagree")),
        ],
    ]
)

cancel_key = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Ortga", callback_data="cancel"),
        ]
    ]
)


# User language

response_callback_lang = CallbackData('language', 'code')
languages = {
    "O'zbek": "uz",
    "Русский": "ru",
    "English": "en",
    "中文": "zh",
    "日本語": "ja",
    "Қазақша": "kk",
    "العربية": "ar",
    "Deutsch": "de",
    "한국어": "ko",
    "Español": "es",
    "فارسی": "fa",
    "Türkçe": "tr",
    "Українська": "uk",
    "हिन्दी": "hi"
}

lang_button = InlineKeyboardMarkup(row_width=2)
for key, value in languages.items():
    lang_button.insert(InlineKeyboardButton(text=key, callback_data=response_callback_lang.new(code=value)))




 
