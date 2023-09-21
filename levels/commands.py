import random
from discord.ext import commands
from db.current import get_levels_db, get_kicks_db
from levels.utils.target import TargetParser
from levels.utils.points import LevelPoints
from levels.utils.kick import LevelKick
from levels.utils.misc import LevelMisc
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

    points = LevelPoints.convert(points)
    await ctx.message.reply(f"У тебя {points} см. " + LevelMisc.phrase(points))


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

    points = [f"{i}. {name}: {LevelPoints.convert(v)} см."
              for i, (p, v) in enumerate(table)
              if (name := members.get(p))]
    await ctx.message.reply('\n'.join(points))


@commands.command(name='выебать')
async def cmd_levels_kick(ctx, *args):
    for i, target in enumerate(TargetParser.parce(args)):
        if LevelKick.get_uses(ctx.channel.id, ctx.author.id) >= LevelKick.MAX_KICK_USES:
            await ctx.message.reply("Ты уже выебал 3 раза, возвращайся через полдня!")
            return

        members = LevelMisc.get_members(ctx.channel)
        member_ids = {m.id: 1 for m in members}

        if not member_ids.get(target.id):
            await ctx.message.reply(f'{i}. <@{target.id}> выебать невозможно!')
            continue

        target_id = target.id if target.id else random.choice(members).id
        pts = LevelKick.execute(ctx.channel.id, ctx.author.id, target_id)
        LevelKick.add_use(ctx.channel.id, ctx.author.id)

        await ctx.message.reply(f"{i}. Ты подкрадываешься к <@{target_id}> и делаешь {random.randint(1, 10)} фрикций, "
                                f"получив {LevelPoints.convert(pts):.2f} см.")


@commands.command(name='args')
async def cmd_args_test(ctx, *args):
    await ctx.channel.send([str(t) for t in TargetParser.parce(args)])


@commands.command(name='circle')
async def circle(ctx):
    members = LevelMisc.get_members(ctx.channel)
    report = Events.circle(ctx.channel.id, members)
    await ctx.message.reply(report)


@commands.command(name='alltoone')
async def alltoone(ctx):
    members = LevelMisc.get_members(ctx.channel)
    report = Events.all_to_one(ctx.channel.id, members)
    await ctx.message.reply(report)


@commands.command(name='cut')
async def cut(ctx):
    members = LevelMisc.get_members(ctx.channel)
    report = Events.cut(ctx.channel.id, members)
    await ctx.message.reply(report)


@commands.command(name='кто')
async def who(ctx):
    level_daily_event.start(ctx)
