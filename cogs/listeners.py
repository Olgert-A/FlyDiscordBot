import logging

from discord.ext import commands, tasks
from db.current import get_levels_db, get_rolls_db
from levels.utils.points import LevelPoints
from levels.tasks import kicks_daily_clear, level_daily_event, roll_points_event

logging.basicConfig(level=logging.INFO)


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def bot_init(self):
        await self.bot.tree.sync()

        def tack_starter(task_coroutine, params=None):
            task = task_coroutine.get_task()
            if task and not task.done():
                logging.info(f"task {task_coroutine} already runned!")
                return
            if params:
                task_coroutine.start(params)
            else:
                task_coroutine.start()
            logging.info(f"task {task_coroutine} is starting!")

        tack_starter(kicks_daily_clear)
        #kicks_daily_clear.start()
        channels = [self.bot.get_channel(channel_id) for channel_id in get_levels_db().get_channels()]
        #level_daily_event.start(channels)
        tack_starter(level_daily_event, channels)
        guilds = [self.bot.get_guild(guild_id) for guild_id in get_rolls_db().get_guilds()]
        tack_starter(roll_points_event, guilds)
        #roll_points_event.start(guilds)


    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"{self.bot.user.name} connected.")
        await self.bot_init()

    @commands.Cog.listener()
    async def on_resumed(self):
        logging.info(f"{self.bot.user.name} resumed.")
        await self.bot_init()

    @commands.Cog.listener()
    async def on_shard_ready(self):
        logging.info(f"{self.bot.user.name} shard ready.")
        await self.bot_init()

    @commands.Cog.listener()
    async def on_shard_resumed(self):
        logging.info(f"{self.bot.user.name} shard resumed.")
        await self.bot_init()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            get_levels_db().points_add(message.channel.id, message.author.id, LevelPoints.generate())


async def setup(bot: commands.Bot):
    await bot.add_cog(ListenerCog(bot))
