import os
import discord
import logging
import random
from discord.ext import commands
from commands.register import to_use
from db.current import get_levels_db
from levels.utils.points import LevelPoints
from levels.tasks import kicks_daily_clear, level_daily_event

logging.basicConfig(level=logging.INFO)


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @client.tree.command(name='test', description='Find hof1k % in yourself')
    async def test(ctx: discord.Interaction):
        await ctx.response.send_message(f"Сегодня ты хофик на {random.randint(0, 100)}%!")

    @client.event
    async def on_ready():
        print(f"{client.user.name} connected.")
        try:
            synced = await client.tree.sync()
            logging.info(f'Sync result = {synced}')
        except Exception as e:
            logging.exception(e)

        kicks_daily_clear.start()
        channels = [client.get_channel(channel_id) for channel_id in get_levels_db().get_channels()]
        level_daily_event.start(channels)

    @client.tree.command(name='hello')
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message('Slash hello')

    @client.event
    async def on_message(message):
        await client.process_commands(message)

        # logging.info(message)

        if not message.author.bot:
            get_levels_db().points_add(message.channel.id, message.author.id, LevelPoints.generate())

    for cmd in to_use:
        client.add_command(cmd)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
