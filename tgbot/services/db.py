from typing import Union
from tgbot.config import load_config
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

config = load_config(".env")

class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        # conn = await asyncpg.connect(config.DB_URL)
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    # Users table queries

    async def add_user(self, full_name, username, telegram_id, credits, is_premium, language_code, joined_date):
        sql = "INSERT INTO savebot_telegramusers (full_name, username, telegram_id, language_code, credits, is_premium, joined_date) VALUES($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, full_name, username, telegram_id, language_code, credits, is_premium, joined_date, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM savebot_telegramusers"
        return await self.execute(sql, fetch=True)
    
    async def select_all_uz_users(self):
        sql = "SELECT * FROM savebot_telegramusers WHERE language_code=uz"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM savebot_telegramusers WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM savebot_telegramusers"
        return await self.execute(sql, fetchval=True)

    async def count_users_by_language(self):
        sql = "SELECT COUNT(*) FROM savebot_telegramusers WHERE 'language_code'=uz"
        return await self.execute(sql, fetchval=True)

    async def users_joined_today(self):
        sql = """SELECT COUNT(*) FROM savebot_telegramusers WHERE joined_date
                 IN(SELECT joined_date FROM savebot_telegramusers WHERE
                 date_trunc('day', joined_date) = date_trunc('day', current_date))"""
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE savebot_users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def set_language_code(self, language_code, telegram_id):
        sql = "UPDATE savebot_telegramusers SET language_code=$1 WHERE telegram_id=$2"
        return await self.execute(sql, language_code, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM savebot_users WHERE TRUE", execute=True)

    async def get_credits(self, telegram_id):
        sql = "SELECT credits FROM savebot_telegramusers WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def consume_credits(self, telegram_id):
        sql = "UPDATE savebot_telegramusers SET credits=credits - 1 WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, execute=True)

    async def update_credits(self):
        sql = "UPDATE savebot_telegramusers SET credits=25"
        return await self.execute(sql, execute=True)

    # Channels table queries

    async def get_all_channels(self):
        sql = "SELECT username FROM savebot_channels"
        return await self.execute(sql, fetch=True)

    async def select_all_channels(self):
        sql = "SELECT * FROM savebot_channels"
        return await self.execute(sql, fetch=True)

    # Apicalls table queries

    async def add_api_request(self, name, status, created_at):
        sql = "INSERT INTO savebot_apicalls (name, status, created_at) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, name, status, created_at, fetchrow=True)
    
    async def count_api_request(self):
        sql = """SELECT name, COUNT(*) FROM savebot_apicalls WHERE created_date 
                 IN(SELECT created_date FROM savebot_apicalls WHERE date_trunc('month', created_date) = date_trunc('month', current_date))
                 GROUP BY name"""
        return await self.execute(sql, fetch=True)
    

    # Invite Link queries

    async def add_invite_link(self, name, created_at):
        sql = "INSERT INTO savebot_invitelink (name, created_at) VALUES($1, $2) returning *"
        return await self.execute(sql, name, created_at, fetchrow=True)

db = Database()