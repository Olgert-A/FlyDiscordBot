import os
import discord
import logging
import asyncio
from discord.ext import commands

logging.basicConfig(level=logging.INFO)


async def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    cogs = ['cogs.fun', 'cogs.listeners', 'cogs.levels']
    for cog in cogs:
        await client.load_extension(cog)

    await client.start(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    asyncio.run(main())

