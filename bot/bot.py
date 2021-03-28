from config import Config
from pathlib import Path

import discord
from db import database
from discord.ext import commands

class MusicBot(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        self.db = database.Database(Config.DSN)

        super().__init__(command_prefix=self.prefix, case_insensitive=True, intents=discord.Intents.all())

    def setup(self):
        print("Running setup...")
    
        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            print(f" Loaded extension '{cog}'")

        print("Setup complete.")

    def run(self):
        self.setup()

        with open("secrets/token", "r", encoding="utf-8") as f:
            TOKEN = f.read()

        print("Running bot...")
        super().run(TOKEN, reconnect=True)

    async def shutdown(self):
        print("Closing connection to Discord...")
        await super().close()

    async def close(self):
        print("Shutting down on keyboard interrupt...")
        await self.shutdown()

    async def on_connect(self):
        print(f"  Connected to Discord (latency: {self.latency*1000:,.0f} ms)")

    async def on_resume(self):
        print("Bot resumed")

    async def on_disconnect(self):
        print("Bot disconnected")

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        print("Bot ready")

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or(self._fetch_prefix())(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)
        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    def _fetch_prefix(self, message):
        id = message.guild.id
        prefix = self.db.field("SELECT cmd_prefix FROM guild WHERE guild_id = $1", id)
        if prefix is None:
            return Config.DEFAULT_PREFIX
        return prefix

