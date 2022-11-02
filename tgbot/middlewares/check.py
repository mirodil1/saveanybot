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
        sub_msg_en = "Please, subscribe to the following channels to use bot."
        sub_msg_ar = ".من فضلك ، اشترك في القنوات التالية لاستخدام البوت"
        sub_msg_de = "Bitte abonnieren Sie die folgenden Kanäle, um Bot zu verwenden."
        sub_msg_es = "Por favor, suscríbase a los siguientes canales para usar el bot."
        sub_msg_fa = "لطفا برای استفاده از ربات در کانال های زیر مشترک شوید"
        sub_msg_hi = "कृपया बॉट का उपयोग करने के लिए निम्नलिखित चैनलों की सदस्यता लें"
        sub_msg_ja = "ボットを使用するには、次のチャンネルに登録してください。"
        sub_msg_kk = "Ботты пайдалану үшін келесі арналарға жазылыңыз."
        sub_msg_ko = "봇을 사용하려면 다음 채널을 구독하십시오."
        sub_msg_ru = "Пожалуйста, подпишитесь на следующие каналы, чтобы использовать бота."
        sub_msg_tr = "Bot kullanmak için lütfen aşağıdaki kanallara abone olunuz."
        sub_msg_uk = "Щоб використовувати бота, підпишіться на наступні канали."
        sub_msg_uz = "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling"
        sub_msg_zh = "請訂閱以下頻道以使用機器人。"

        credits_msg_en = "Your limit for today is over."
        credits_msg_ar = ".الحد الخاص بك لهذا اليوم قد انتهى"
        credits_msg_de = "Schnell und einfach herunterladen."
        credits_msg_es = "Su límite para hoy ha terminado."
        credits_msg_fa = "محدودیت امروز شما تمام شده است"
        credits_msg_hi = "आज के लिए आपकी सीमा समाप्त हो गई है"
        credits_msg_ja = "今日の制限を超えています。"
        credits_msg_kk = "Бүгінгі шектеуіңіз аяқталды."
        credits_msg_ko = "오늘의 한도는 끝났습니다."
        credits_msg_ru = "Ваш лимит на сегодня исчерпан."
        credits_msg_tr = "Your limit for today is over."
        credits_msg_uk = "Ваш ліміт на сьогодні вичерпано."
        credits_msg_uz = "Bugungi limitingiz tugadi."
        credits_msg_zh = "你今天的限額已經結束。"


        welcome_msg_en = "Your limit for today is over."
        welcome_msg_ar = "<b> أرسل ارتباطًا واحصل على الوسائط الخاصة بك! </b>\n\nيمكنك تنزيل ملفات الصور والفيديو من الوسائط الاجتماعية الشهيرة!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_de = "<b>Senden Sie einen Link und erhalten Sie Ihre Medien!</b>\n\nSie können Foto- und Videodateien von beliebten sozialen Medien herunterladen!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_es = "<b>Envía un enlace y obtén tus medios!</b>\n\nPuedes descargar archivos de fotos y videos de las redes sociales populares!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_fa = "<b>یک پیوند ارسال کنید و رسانه خود را دریافت کنید!</b>\n\nمی‌توانید فایل‌های عکس و ویدیو را از رسانه‌های اجتماعی محبوب دانلود کنید!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_hi = "<b>एक लिंक भेजें और अपना मीडिया प्राप्त करें!</b>\n\nआप लोकप्रिय सोशल मीडिया से फ़ोटो और वीडियो फ़ाइलें डाउनलोड कर सकते हैं!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_ja = "<b>リンクを送信してメディアを入手しましょう!</b>\n\n人気のソーシャル メディアから写真やビデオ ファイルをダウンロードできます!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_kk = "<b>Сілтемені жіберіп, медиа файлдарыңызды алыңыз!</b>\n\nТанымал әлеуметтік желілерден фотосуреттер мен бейнелерді жүктеп алуға болады!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_ko = "<b>링크를 보내고 미디어를 받으세요!</b>\n\n인기 있는 소셜 미디어에서 사진 및 비디오 파일을 다운로드할 수 있습니다!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_ru = "<b>Отправьте ссылку и получите свои медиафайлы!</b>\n\nВы можете скачать фото и видео файлы из популярных социальных сетей!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_tr = "<b>Bir bağlantı gönderin ve medyanızı alın!</b>\n\nPopüler sosyal medyadan fotoğraf ve video dosyaları indirebilirsiniz!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_uk = "<b>Надішліть посилання та отримайте медіафайли!</b>\n\nВи можете завантажувати фото- та відеофайли з популярних соціальних мереж!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_uz = "<b>Havola jo'nating va yuklab oling!</b>\n\nMashhur ijtimoiy tarmoqlardan rasm va videolarni yuklab olishingiz mumkin!\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"
        welcome_msg_zh = "<b>發送鏈接並獲取您的媒體！</b>\n\n您可以從流行的社交媒體下載照片和視頻文件！\n\nInstagram\nTikTok\nFacebook\nYouTube\nTwitter\nVkontakte\nSnapChat"


        sub_msg = {
            "uz": sub_msg_uz,
            "ru": sub_msg_ru,
            "en": sub_msg_en,
            "zh": sub_msg_zh,
            "ja": sub_msg_ja,
            "kk": sub_msg_kk,
            "ar": sub_msg_ar,
            "de": sub_msg_de,
            "ko": sub_msg_ko,
            "es": sub_msg_es,
            "fa": sub_msg_fa,
            "tr": sub_msg_tr,
            "uk": sub_msg_uk,
            "hi": sub_msg_hi,
        }

        credit_msg = {
            "uz": credits_msg_uz,
            "ru": credits_msg_ru,
            "en": credits_msg_en,
            "zh": credits_msg_zh,
            "ja": credits_msg_ja,
            "kk": credits_msg_kk,
            "ar": credits_msg_ar,
            "de": credits_msg_de,
            "ko": credits_msg_ko,
            "es": credits_msg_es,
            "fa": credits_msg_fa,
            "tr": credits_msg_tr,
            "uk": credits_msg_uk,
            "hi": credits_msg_hi,
        }

        welcome_msg = {
            "uz": welcome_msg_uz,
            "ru": welcome_msg_ru,
            "en": welcome_msg_en,
            "zh": welcome_msg_zh,
            "ja": welcome_msg_ja,
            "kk": welcome_msg_kk,
            "ar": welcome_msg_ar,
            "de": welcome_msg_de,
            "ko": welcome_msg_ko,
            "es": welcome_msg_es,
            "fa": welcome_msg_fa,
            "tr": welcome_msg_tr,
            "uk": welcome_msg_uk,
            "hi": welcome_msg_hi,
        }

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
                    await update.callback_query.message.edit_text(text=welcome_msg[user['language_code']])
                else:
                    await update.callback_query.answer(text=sub_msg[user['language_code']], show_alert=True)
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
                    await update.message.answer(text=sub_msg[user['language_code']], disable_web_page_preview=True, reply_markup=await subscription_button(channels, user))
                    raise CancelHandler()
                except:
                    raise CancelHandler()
        if credits['credits'] <= 0:
            try:
                await update.message.answer(text=credit_msg[user['language_code']])
                raise CancelHandler()
            except:
                raise CancelHandler()