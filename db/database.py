import asyncio
import asyncpg


class Database:

    pool = None

    def __init__(self, dsn):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_async(dsn))

    async def init_async(self, dsn):
        Database.pool = await asyncpg.create_pool(dsn)

    async def get_pool(self):
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
        async with self.get_pool() as conn:
            return await conn.fetchval(sql, *values)
        
    async def record(self, sql, *values):
        async with self.get_pool() as conn:
            return await conn.fetchrow(sql, *values)

    async def records(self, sql, *values):
        async with self.get_pool() as conn:
            return await conn.fetch(sql, *values)

    async def column(self, sql, *values):
        async with self.get_pool() as conn:
            rows = await conn.fetch(sql, *values)
            return [row[0] for row in rows]

    async def execute(self, sql, *values):
        async with self.get_pool() as conn:
            await conn.execute(sql, *values)

    async def executemany(self, sql, valueset):
        async with self.get_pool() as conn:
            await conn.executemany(sql, valueset)   