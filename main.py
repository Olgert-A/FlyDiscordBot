import os
import discord
import logging
import asyncio
from discord.ext import commands
from commands.register import register_commands
from db.current import get_levels_db
from levels.tasks import kicks_daily_clear, level_daily_event

logging.basicConfig(level=logging.INFO)
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@client.event
async def on_ready(self):
    logging.info(f"{self.bot.user.name} connected.")
    cogs = ['cogs.listeners', 'cogs.fun']
    for cog in cogs:
        await self.bot.load_extension(cog)

    await self.bot.tree.sync()

    kicks_daily_clear.start()
    channels = [self.bot.get_channel(channel_id) for channel_id in get_levels_db().get_channels()]
    level_daily_event.start(channels)


def main():
    register_commands(client)
#    await register_cogs(client)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()


