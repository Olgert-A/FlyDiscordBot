import asyncio
import random
import logging
from discord.ext import commands
from db.current import get_levels_db, get_kicks_db
from levels.utils.target import TargetParser, TargetKicks
from levels.utils.points import LevelPoints
from levels.utils.kick import LevelKick
from levels.utils.misc import LevelMisc
from levels.events import LevelEvents
from levels.tasks import level_daily_event

logging.basicConfig(level=logging.INFO)


@commands.command(name='лвл-рег')
async def cmd_levels_reg(ctx):
    channel_id = ctx.channel.id
    get_levels_db().channel_reg(channel_id)
    members = LevelMisc.get_members(channel_id)
    for m in members:
        get_levels_db().points_add(channel_id, m.id, 0)
        get_kicks_db().add(channel_id, m.id, 0)

    level_daily_event.start(ctx)

    await ctx.message.delete()
    await ctx.channel.send(f"""Канал зарегистрирован в программе **Ебырьметр**! Каждое сообщение пользователя может как повысить, так и понизить уровень. 
    !ебырь - вывод твоего уровня 
    !ебыри - таблица уровней""")


@commands.command(name='лвл-стоп')
async def cmd_levels_stop(ctx):
    get_levels_db().channel_reg_stop(ctx.channel.id)
    level_daily_event.stop()
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
    if LevelKick.get_uses(ctx.channel.id, ctx.author.id) >= LevelKick.MAX_KICK_USES:
        await ctx.message.reply("Ты уже выебал 3 раза, возвращайся через полдня!")
        return

    parsed = TargetParser.parce(args)
    targets = parsed if parsed else [TargetKicks('1')]

    members = LevelMisc.get_members(ctx.channel)
    member_ids = {f'{m.id}': 1 for m in members}
    logging.info(member_ids)

    for target in targets:
        logging.info(target)
        if target.id and not member_ids.get(target.id):
            await ctx.message.reply(f'<@{target.id}> выебать невозможно!')
            continue

        for _ in range(target.kicks):
            if LevelKick.get_uses(ctx.channel.id, ctx.author.id) >= LevelKick.MAX_KICK_USES:
                await ctx.message.reply("Ты уже выебал 3 раза, возвращайся через полдня!")
                return

            target_id = target.id if target.id else random.choice(members).id

            pts = LevelKick.execute(ctx.channel.id, ctx.author.id, target_id)
            LevelKick.add_use(ctx.channel.id, ctx.author.id)

            await ctx.message.reply(
                f"Ты подкрадываешься к <@{target_id}> и делаешь {random.randint(1, 10)} фрикций, "
                f"получив {LevelPoints.convert(pts):.2f} см.")


@commands.command(name='ивент')
async def cmd_start_event(ctx):
    pts = -200
    channel_id = ctx.channel.id
    get_levels_db().points_add(channel_id, ctx.author.id, pts)
    await ctx.message.reply(f'Ты тратишь {LevelPoints.convert(pts):.2f} см. и запускаешь случайный ивент!')
    await asyncio.sleep(1)

    event = random.choice(LevelEvents.get_events())
    members = LevelMisc.get_members(channel_id)
    report = event(channel_id, members)
    await ctx.channel.send(report)

@commands.command(name='инфо')
async def cmd_args_info(ctx):
    await ctx.message.reply(
        """Каждое сообщение пользователя может как повысить, так и понизить уровень. 
!ебырь - вывод твоего уровня 
!ебыри - таблица уровней
!выебать <тег цели> <число раз> - выебать тегнутого участника заданное количество раз.

Можно выебать 3 раза в полдня, сброс использований происходит в 6 мск.
По-умолчанию число раз = 1 и может не указываться. 
Можно указывать несколько тегов через пробел. 
Число раз без тега выберет данное число рандомных участников и выебет.
    
Пример ебки (вместо имён должны быть теги):
!выебать 3 - выебет 3 рандомных
!выебать 1 коляс 2 - выебет 1 рандомного и дважды коляса
!выебать ольгерт айваз хофик - выебет указанных по 1 разу
!выебать коляс хаханим 2 - выебет 1 раз коляса и 2 раза хаханим
!выебать айваз любойтекст 2 - выебет 1 раз айваза и 2 рандомов"""
    )

