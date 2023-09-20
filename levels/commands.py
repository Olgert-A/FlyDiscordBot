import random
from discord.ext import commands
from db.current import get_levels_db, get_kicks_db
from levels.utils import LevelUtils as Utils


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
    uses = get_kicks_db().get(ctx.channel.id, ctx.author.id)

    if uses and uses >= 3:
        await ctx.message.reply("Ты уже выебал 3 раза, возвращайся через полдня!")
        return

    def get_target_id():
        members = [m for m in ctx.channel.members if not m.bot]
        if target:
            # if m.id in target return m.id else return None
            for m in members:
                if str(m.id) in target:
                    return m.id
        else:
            return random.choice(members).id

    if not (target_id := get_target_id()):
        await ctx.message.reply("Тегни цель, еблан")
        return

    pts_up = Utils.calc_kick(ctx.channel.id, ctx.author.id, target_id)

    get_levels_db().points_add(ctx.channel.id, ctx.author.id, pts_up)
    get_levels_db().points_add(ctx.channel.id, target_id, -pts_up)
    get_kicks_db().add(ctx.channel.id, ctx.author.id, 1)
    await ctx.message.reply(f"Ты подкрадываешься к <@{target_id}> и делаешь {random.randint(1, 10)} фрикций, "
                            f"получив {Utils.convert_points(pts_up):.2f} см.")

