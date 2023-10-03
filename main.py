import os
import discord
import logging
import asyncio
from discord.ext import commands
from commands.register import register_commands

logging.basicConfig(level=logging.INFO)
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def main():

    #cogs = ['cogs.listeners']
    #for cog in cogs:
    #    await client.load_extension(cog)

    register_commands(client)
#    await register_cogs(client)
    await client.start(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    asyncio.run(main())


