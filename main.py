import os
import discord
from discord.ext import commands
from commands.register import to_use


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f"{client.user.name} connected.")

    for cmd in to_use:
        client.add_command(cmd)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
