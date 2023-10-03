import os
import discord
import logging
from discord.ext import commands
from commands.register import register_commands
from cogs.registerer import register_cogs


logging.basicConfig(level=logging.INFO)


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    register_commands(client)
    register_cogs(client)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
