import logging

from discord.ext import commands
from db.current import get_levels_db
from levels.utils.points import LevelPoints
from levels.tasks import kicks_daily_clear, level_daily_event

logging.basicConfig(level=logging.INFO)


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"{self.bot.user.name} connected.")

        await self.bot.tree.sync()

        kicks_daily_clear.start()
        channels = [self.bot.get_channel(channel_id) for channel_id in get_levels_db().get_channels()]
        level_daily_event.start(channels)

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)

        if not message.author.bot:
            get_levels_db().points_add(message.channel.id, message.author.id, LevelPoints.generate())


async def setup(bot: commands.Bot):
    await bot.add_cog(ListenerCog(bot))
