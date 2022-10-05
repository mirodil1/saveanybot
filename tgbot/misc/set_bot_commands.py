from aiogram import types

async def set_default_commands(bot):
        await bot.set_my_commands(
        
            [
                types.BotCommand("start", "Restart bot"),
                types.BotCommand("lang", "Change language"),
            ]
        )