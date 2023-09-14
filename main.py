import os
import discord
import datetime
from discord.ext import commands, tasks
from commands.register import to_use
from db.current import get_db, get_uses_db
from levels.commands import random_points


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f"{client.user.name} connected.")
        kicks_daily_clear.start()

    @tasks.loop(hours=12, time=datetime.time(hour=13))
    async def kicks_daily_clear():
        uses_db = get_uses_db()
        uses_db.clear()

    @client.event
    async def on_message(message):
        await client.process_commands(message)

        if not message.author.bot:
            get_db().points_add(message.channel.id, message.author.id, random_points())

    for cmd in to_use:
        client.add_command(cmd)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
