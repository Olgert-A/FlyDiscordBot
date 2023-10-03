import os
import discord
import logging
import asyncio
from discord.ext import commands
from commands.register import register_commands
from db.current import get_levels_db
from levels.tasks import kicks_daily_clear, level_daily_event

logging.basicConfig(level=logging.INFO)


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            client.load_extension("cogs." + f[:-3])

    register_commands(client)
    #    await register_cogs(client)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
