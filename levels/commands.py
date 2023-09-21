import random
from discord.ext import commands
from db.current import get_levels_db, get_kicks_db
from levels.utils import LevelUtils as Utils
from levels.events import LevelEvents as Events
from levels.tasks import level_daily_event


@commands.command(name='лвл-рег')
async def cmd_levels_reg(ctx):
    get_levels_db().channel_reg(ctx.channel.id)
    for m in ctx.channel.members:
        if not m.bot:
            get_levels_db().points_add(ctx.channel.id, m.id, 0)
            get_kicks_db().add(ctx.channel.id, m.id, 0)

    await ctx.message.delete()
    await ctx.channel.send(f"""Канал зарегистрирован в программе **Ебырьметр**! Каждое сообщение пользователя может как повысить, так и понизить уровень. 
    !ебырь - вывод твоего уровня 
    !ебыри - таблица уровней""")


@commands.command(name='лвл-стоп')
async def cmd_levels_stop(ctx):
    get_levels_db().channel_reg_stop(ctx.channel.id)
    await ctx.message.delete()
    await ctx.channel.send(f"Канал больше не участвует в программе **Ебырьметр**")


@commands.command(name='ебырь')
async def cmd_levels_points(ctx):
    if not (points := get_levels_db().points_get(ctx.channel.id, ctx.author.id)):
        await ctx.message.reply(f"Sasi <:pepe_loh:1022083481725063238>")
        return

    points = Utils.convert_points(points)
    await ctx.message.reply(f"У тебя {points} см. " + Utils.phrase(points))


@commands.command(name='ебыри')
async def cmd_levels_table(ctx):
    def name(member):
        if member.nick:
            return member.nick
        elif member.global_name:
            return member.global_name
        else:
            return member.name

    members = {m.id: name(m) for m in ctx.channel.members if not m.bot}
    table = get_levels_db().points_table(ctx.channel.id)

    if not table:
        await ctx.message.reply(f"Sasi <:pepe_loh:1022083481725063238>")
        return

    table = sorted(table.items(), key=lambda v: v[1], reverse=True)

    points = [f"{i}. {name}: {Utils.convert_points(v)} см."
              for i, (p, v) in enumerate(table)
              if (name := members.get(p))]
    await ctx.message.reply('\n'.join(points))


@commands.command(name='выебать')
async def cmd_levels_kick(ctx, target=None):
    if Utils.get_kicks_use(ctx.channel.id, ctx.author.id) >= Utils.MAX_KICK_USES:
        await ctx.message.reply("Ты уже выебал 3 раза, возвращайся через полдня!")
        return

    members = Utils.get_members(ctx.channel)
    target_id = Utils.get_target_id(target, members) if target else random.choice(members).id

    if not target_id:
        await ctx.message.reply("Тегни цель, еблан")
        return

    report = Utils.kick(ctx.channel.id, ctx.author.id, target_id)
    await ctx.message.reply(report)


@commands.command(name='circle')
async def circle(ctx):
    members = Utils.get_members(ctx.channel)
    report = Events.circle(ctx.channel.id, members)
    await ctx.message.reply(report)


@commands.command(name='alltoone')
async def alltoone(ctx):
    members = Utils.get_members(ctx.channel)
    report = Events.all_to_one(ctx.channel.id, members)
    await ctx.message.reply(report)


@commands.command(name='cut')
async def cut(ctx):
    members = Utils.get_members(ctx.channel)
    report = Events.cut(ctx.channel.id, members)
    await ctx.message.reply(report)


@commands.command(name='кто')
async def who(ctx):
    level_daily_event.start(ctx)
