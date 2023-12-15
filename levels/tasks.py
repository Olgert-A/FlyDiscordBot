import datetime
import random
from typing import List
import discord
from discord.ext import tasks
from db.current import get_kicks_db, get_events_db, get_rolls_db
from levels.events import LevelEvents
from levels.utils.misc import LevelMisc

utc = datetime.timezone.utc


@tasks.loop(time=[datetime.time(hour=3, tzinfo=utc),
                  datetime.time(hour=15, tzinfo=utc)])
async def kicks_daily_clear():
    uses_db = get_kicks_db()
    uses_db.clear()


@tasks.loop(time=datetime.time(hour=15, tzinfo=utc))
async def level_daily_event(channels):
    get_events_db().clear()

    for channel in channels:
        event = random.choice(LevelEvents.get_events())
        members = LevelMisc.get_members(channel)
        report = event(channel.id, members)
        await channel.send(report)


@tasks.loop(time=datetime.time(minute=5, tzinfo=utc))
async def roll_points_event(guilds: List[discord.Guild]):
    for guild in guilds:
        for member in guild.members:
            if not member.bot:
                pass
                #get_rolls_db().points_add(guild.id, member.id, 100)
