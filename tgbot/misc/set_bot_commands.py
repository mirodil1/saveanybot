from aiogram import types
from tgbot.middlewares.i18n import _

async def set_default_commands(bot):
        await bot.set_my_commands(

            [
                types.BotCommand("start", _("Restart bot")),
                types.BotCommand("lang", _("Change language")),

            ]
        )