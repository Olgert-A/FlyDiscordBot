import datetime
import random
from discord.ext import tasks
from db.current import get_kicks_db
from levels.events import LevelEvents

utc = datetime.timezone.utc


@tasks.loop(time=[datetime.time(hour=3, tzinfo=utc),
                  datetime.time(hour=15, tzinfo=utc)])
async def kicks_daily_clear():
    uses_db = get_kicks_db()
    uses_db.clear()


@tasks.loop(minutes=1)
async def level_daily_event(ctx):
    event = random.choice(LevelEvents.get_events())
    members = [m for m in ctx.channel.members if not m.bot]
    event(ctx.channel.id, members)
