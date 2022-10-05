from typing import Any, Tuple, Dict, Optional
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from pathlib import Path
from babel import Locale
from tgbot.services.db import db
import asyncpg

class CustomI18nMiddleware(I18nMiddleware):
    def __init__(self, domain, path=None, **kwargs):
        super().__init__(domain, path)
        self.kwargs = kwargs
        self.domain = domain
        self.path = path

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user: Optional[types.User] = types.User.get_current()
        locale: Optional[Locale] = user.locale if user else None
        try:
            user = await db.select_user(telegram_id = user['id'])
            language = user['language_code']
        except:
            pass
        if language in self.locales:
            return language
        # return self.default
        elif locale and locale.language in self.locales:
            *_, data = args
            language = data['locale'] = locale.language
            return language
        return self.default


BASE_DIR = Path(__file__).parent
LOCALES_DIR ='locales'

_ = i18n = CustomI18nMiddleware("savebot", LOCALES_DIR)