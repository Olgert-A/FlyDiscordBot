import os
import discord
import logging
import asyncio
from discord.ext import commands
from commands.register import register_commands
from cogs.registerer import register_cogs


logging.basicConfig(level=logging.INFO)


async def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    register_commands(client)
    await register_cogs(client)
    await client.start(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

