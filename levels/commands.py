import random
from discord.ext import commands
from levels.db import LevelsDB


def phrase(points):
    phrases = {(-1000, 0): ["Отрицательный? Ты точно мужик?",
                            "Как вообще можно отрастить минусовой член?",
                            "На доске Позор года висит твоя фотография."],
               (0, 10): ["Команда исследователей США создали микроскоп, чтобы разглядеть твоё достоинство.",
                    "Возможно, у тебя азиатские корни.",
                    "Натирай три раза в день свой корень, и уже через неделю он окрепнет и вырастет. Или опухнет.",
                    "Маловат, надеюсь, у тебя в жизни есть другой повод для гордости."]}

    for (start, end), v in phrases.items():
        if start <= points < end:
            return random.choice(v)


def convert_points(points):
    return points / 50.


def random_points():
    return random.randint(-10, 10)


@commands.command(name='лвл_рег')
async def cmd_levels_reg(ctx):
    LevelsDB().channel_reg(ctx.channel.id)
    for m in ctx.channel.members:
        if not m.bot:
            LevelsDB().points_add(ctx.channel.id, m.id, random_points())

    await ctx.message.delete()
    await ctx.channel.send(f"""Канал зарегистрирован в программе **Ебырьметр**! Каждое сообщение пользователя может как повысить, так и понизить уровень. 
    !ебырь - вывод твоего уровня 
    !ебыри - таблица уровней""")


@commands.command(name='лвл_стоп')
async def cmd_levels_stop(ctx):
    LevelsDB().channel_unreg(ctx.channel.id)
    await ctx.message.delete()
    await ctx.channel.send(f"Канал больше не участвует в программе **Ебырьметр**")


@commands.command(name='ебырь')
async def cmd_levels_points(ctx):
    if not (points := LevelsDB().points_get(ctx.channel.id, ctx.author.id)):
        await ctx.message.reply(f"Канал не зарегистрирован в программе **Ебырьметр**")
        return

    points = convert_points(points)
    await ctx.message.reply(f"У тебя {points} см. " + phrase(points))


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
    table = LevelsDB().points_table(ctx.channel.id)
    if not table:
        await ctx.message.reply(f"Канал не зарегистрирован в программе **Ебырьметр**")
        return

    points = [f"{i}. {name}: {convert_points(v)} см."
              for i, (p, v) in enumerate(table.items())
              if (name := members.get(p))]
    await ctx.message.reply('\n'.join(points))
