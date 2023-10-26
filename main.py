import os
import discord
import logging
import asyncio
from discord.ext import commands
from cogs.registerer import register_cogs


logging.basicConfig(level=logging.INFO)


async def main():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    await register_cogs(bot)
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    asyncio.run(main())

