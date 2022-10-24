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

btn_text_en = "✅ Subscribed"
btn_text_ar = "✅ اشتركت"
btn_text_de = "✅ Ich habe abonniert"
btn_text_es = "✅ Me suscribí"
btn_text_fa = "✅ من مشترک شدم"
btn_text_hi = "✅ मैंने सदस्यता ली"
btn_text_ja = "✅ 購読しました"
btn_text_kk = "✅ Жазылдым"
btn_text_ko = "✅ 나는 구독했다"
btn_text_ru = "✅ Подписался"
btn_text_tr = "✅ Abone oldum"
btn_text_uk = "✅ Підписався"
btn_text_uz = "✅ Obuna bo'ldim"
btn_text_zh = "✅ 訂閱"


btn_text = {
        "uz": btn_text_uz,
        "ru": btn_text_ru,
        "en": btn_text_en,
        "zh": btn_text_zh,
        "ja": btn_text_ja,
        "kk": btn_text_kk,
        "ar": btn_text_ar,
        "de": btn_text_de,
        "ko": btn_text_ko,
        "es": btn_text_es,
        "fa": btn_text_fa,
        "tr": btn_text_tr,
        "uk": btn_text_uk,
        "hi": btn_text_hi,
    }


async def subscription_button(channels, user):

    markup = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        if ch['status']:
            status = await check_user_sub(user_id=user['telegram_id'], channel=ch['username'])
        try:
            channel = await bot.get_chat(ch['username'])
        except:
            pass
        if not status:
            markup.insert(
                InlineKeyboardButton(text="{title}".format(title=channel.title), url= ch['invite_link'])
            )
    markup.insert(
        InlineKeyboardButton(text=btn_text[user['language_code']], callback_data="check_subs")
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

 
async def download_button(url):

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(
        InlineKeyboardButton(text=_("Download"), url=url)
    )
    return markup