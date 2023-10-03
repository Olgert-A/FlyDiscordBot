import os
import discord
import logging
import asyncio
from discord.ext import commands
from commands.register import register_commands

logging.basicConfig(level=logging.INFO)


async def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await client.load_extension(f'cogs.{file[:-3]}')

    register_commands(client)
#    await register_cogs(client)
    await client.start(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    asyncio.run(main())


