from typing import Any, Tuple, Optional
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from pathlib import Path
from babel import Locale
from tgbot.services.db import db


class CustomI18nMiddleware(I18nMiddleware):
    def __init__(self, domain, path=None, **kwargs):
        super().__init__(domain, path)
        self.kwargs = kwargs
        self.domain = domain
        self.path = path

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user: Optional[types.User] = types.User.get_current()
        try:
            call_data = args[0]['data'].split(":")
            if call_data[0] == "language":
                await db.set_language_code(language_code=call_data[1], telegram_id=user['id'])
        except:
            pass
        try:
            user = await db.select_user(telegram_id = user['id'])
        except:
            user = None
        if user is not None:
            language = user['language_code']
            if language in self.locales:
                return language
            elif args[1].get('locale') in self.locales:
                language = args[1]['locale']
                return language
        return self.default


BASE_DIR = Path(__file__).parent
LOCALES_DIR ='locales'

_ = i18n = CustomI18nMiddleware("savebot", LOCALES_DIR)