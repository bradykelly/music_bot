import asyncio
import asyncpg


class Database:

    pool = None

    def __init__(self, bot, dsn):
        self.bot = bot
        self.dsn = dsn
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_async(dsn))

    async def init_async(self, dsn):
        Database.pool = await asyncpg.create_pool(dsn)

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get_connection(self):
        return await Database.pool.acquire()

    async def sync(self):
        # Insert.
        await self.executemany("INSERT INTO guild (guild_id) VALUES ($1) ON CONFLICT DO NOTHING", [(g.id,) for g in self.bot.guilds])              

        # Remove.
        stored = await self.column("SELECT guild_id FROM guild")
        member_of = [g.id for g in self.bot.guilds]
        removals = [(g_id,) for g_id in set(stored) - set(member_of)]
        await self.executemany("DELETE FROM guild WHERE guild_id = $1", removals)        

    async def field(self, sql, *values):
        conn = await self.get_connection()
        return await conn.fetchval(sql, *values)
        
    async def record(self, sql, *values):
        conn = await self.get_connection()
        return await conn.fetchrow(sql, *values)

    async def records(self, sql, *values):
        conn = await self.get_connection()
        return await conn.fetch(sql, *values)

    async def column(self, sql, *values):
        conn = await self.get_connection()
        rows = await conn.fetch(sql, *values)
        return [row[0] for row in rows]

    async def execute(self, sql, *values):
        conn = await self.get_connection()
        await conn.execute(sql, *values)

    async def executemany(self, sql, valueset):
        conn = await self.get_connection()
        await conn.executemany(sql, valueset)   