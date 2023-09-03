import os
import discord
import random
from discord.ext import commands
from commands.register import to_use
from levels.db import LevelsDB


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f"{client.user.name} connected.")

    @client.event
    async def on_message(message):
        await client.process_commands(message)

        if not message.author.bot:
            LevelsDB().points_add(message.channel.id, message.author.id, random.randint(-10, 10))

    for cmd in to_use:
        client.add_command(cmd)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
