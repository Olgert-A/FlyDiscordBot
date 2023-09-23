import datetime
import random
from discord.ext import tasks
from db.current import get_kicks_db
from levels.events import LevelEvents
from levels.utils.misc import LevelMisc

utc = datetime.timezone.utc


@tasks.loop(time=[datetime.time(hour=3, tzinfo=utc),
                  datetime.time(hour=15, tzinfo=utc)])
async def kicks_daily_clear():
    uses_db = get_kicks_db()
    uses_db.clear()


@tasks.loop(time=datetime.time(hour=15, tzinfo=utc))
async def level_daily_event(channel):
    event = random.choice(LevelEvents.get_events())
    members = LevelMisc.get_members(channel.id)
    report = event(channel.id, members)
    await channel.send(report)
