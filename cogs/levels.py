import asyncio
import random
import logging
import discord
from discord import app_commands
from discord.ext import commands
from db.current import get_levels_db, get_kicks_db, get_events_db
from levels.utils.target import TargetParser, MemberIdKicks
from levels.utils.points import LevelPoints
from levels.utils.kick import LevelKick
from levels.utils.misc import LevelMisc
from levels.events import LevelEvents
from levels.tasks import level_daily_event

logging.basicConfig(level=logging.INFO)


def check_bot_author_permission():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 776537982924619786

    return app_commands.check(predicate)


class LevelsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='индульгенция',
                          description='Административная команда для сброса ограничения использования команд')
    @check_bot_author_permission()
    @app_commands.rename(what_reset='на-что')
    @app_commands.choices(what_reset=[app_commands.Choice(name='ебку', value=1),
                                      app_commands.Choice(name='ивенты', value=2),
                                      app_commands.Choice(name='всё', value=3)])
    async def reset(self, ctx: discord.Interaction, what_reset: app_commands.Choice[int]):
        if what_reset.value == 1:
            get_kicks_db().clear()
        if what_reset.value == 2:
            get_events_db().clear()
        if what_reset.value == 3:
            get_kicks_db().clear()
            get_events_db().clear()
        await ctx.response.send_message(f"Выдана индульгенция на {what_reset.name}!")

    @app_commands.command(name='дать',
                          description='Административная команда для выдачи поинтов пользователям')
    @check_bot_author_permission()
    @app_commands.rename(target='кому', points='сколько')
    async def give(self, ctx: discord.Interaction, target: discord.Member, points: int):
        if target not in LevelMisc.get_members(ctx.channel):
            await ctx.response.send_message("Этому пользователю нельзя выдать поинты!", ephemeral=True)

        get_levels_db().points_add(ctx.channel.id, target.id, points)
        get_kicks_db().add(ctx.channel.id, target.id, 0)
        get_events_db().add(ctx.channel.id, target.id, 0)
        await ctx.response.send_message("Поинты добавлены!")

    @app_commands.command(name='подключить',
                          description='Административная команда для подключения канала к системе рейтинга')
    @check_bot_author_permission()
    async def levels_reg(self, ctx: discord.Interaction):
        get_levels_db().channel_reg(ctx.channel.id)
        members = LevelMisc.get_members(ctx.channel)
        for m in members:
            get_levels_db().points_add(ctx.channel.id, m.id, 0)
            get_kicks_db().add(ctx.channel.id, m.id, 0)
            get_events_db().add(ctx.channel.id, m.id, 0)

        await ctx.response.send_message(f'Канал зарегистрирован в программе **Ебырьметр**!', ephemeral=True)

    @app_commands.command(name='отключить',
                          description='Административная команда для отключения канала от системы рейтинга')
    @check_bot_author_permission()
    async def levels_stop(self, ctx: discord.Interaction):
        get_levels_db().channel_reg_stop(ctx.channel.id)
        level_daily_event.stop()
        await ctx.response.send_message(f"Канал больше не участвует в программе **Ебырьметр**", ephemeral=True)

    @app_commands.command(name='ебырь',
                          description='Узнай свой рейтинг')
    async def get_points(self, ctx: discord.Interaction):
        if not (points := get_levels_db().points_get(ctx.channel.id, ctx.user.id)):
            await ctx.response.send_message(f"Не удалось получить рейтинг, повтори запрос позже.", ephemeral=True)
            return

        points = LevelPoints.convert(points)
        await ctx.response.send_message(f"У тебя {points} см. " + LevelMisc.phrase(points))

    @app_commands.command(name='ебыри',
                          description='Таблица рейтинга')
    async def get_table(self, ctx: discord.Interaction):
        member_names = {m.id: LevelMisc.name(m) for m in LevelMisc.get_members(ctx.channel)}
        table = get_levels_db().points_table(ctx.channel.id)

        if not table:
            await ctx.response.send_message(f"Не удалось получить таблицу, повтори запрос позже.", ephemeral=True)
            return

        table = sorted(table.items(), key=lambda v: v[1], reverse=True)

        points = [f"{position}. {name}: {LevelPoints.convert(points)} см."
                  for position, (m_id, points) in enumerate(table)
                  if (name := member_names.get(m_id))]
        await ctx.response.send_message('\n'.join(points))

    @app_commands.command(name='выебать',
                          description='Вступить в схватку с кем-то за разницу между вашими рейтингами')
    @app_commands.rename(target_string='цели-ебки')
    @app_commands.describe(target_string='Список парных значений вида <тег цели> <количество ебок>')
    async def kick(self, ctx: discord.Interaction, target_string: str = ''):
        report = ''
        members = LevelMisc.get_members(ctx.channel)
        allowed_to_kick = [m.id for m in members if m.id != ctx.user.id]

        for target in TargetParser.parce(target_string):
            logging.info(target)

            if target.id == MemberIdKicks.TARGET_RANDOM:
                target.id = random.choice(allowed_to_kick)

            for _ in range(target.kicks):
                if LevelKick.get_uses(ctx.channel.id, ctx.user.id) >= LevelKick.MAX_KICK_USES:
                    report += "Ты уже выебал 3 раза, возвращайся через полдня!"
                    await ctx.response.send_message(report)
                    return

                if target.id not in allowed_to_kick:
                    report += f'<@{target.id}> выебать невозможно!\n'
                    break

                pts = LevelKick.execute(ctx.channel.id, ctx.user.id, target.id)
                LevelKick.add_use(ctx.channel.id, ctx.user.id)
                report += f"Ты подкрадываешься к <@{target.id}> и делаешь {random.randint(1, 10)} фрикций, " \
                          f"получив {LevelPoints.convert(pts):.2f} см.\n"

        await ctx.response.send_message(report)

    @app_commands.command(name='ивент',
                          description='Запустить случайный ивент (раз в день, потратив часть рейтинга)')
    async def event(self, ctx: discord.Interaction):
        uses = get_events_db().get(ctx.channel.id, ctx.user.id)
        if uses >= 1:
            await ctx.response.send_message('Ты уже использовал ивент, возвращайся после 18мск!', ephemeral=True)
            return

        pts = -200
        get_levels_db().points_add(ctx.channel_id, ctx.user.id, pts)

        event = random.choice(LevelEvents.get_events())
        members = LevelMisc.get_members(ctx.channel)
        report = event(ctx.channel_id, members)
        if report:
            get_events_db().add(ctx.channel.id, ctx.user.id, 1)
            await ctx.response.send_message(report)
        else:
            get_levels_db().points_add(ctx.channel_id, ctx.user.id, -pts)
            await ctx.response.send_message(f'По каким-то причинам ивент не сработал, поинты возвращены!', ephemeral=True)

    @app_commands.command(name='тест',
                          description='Административная отладочная команда')
    @check_bot_author_permission()
    async def test(self, ctx: discord.Interaction):
        members = LevelMisc.get_members(ctx.channel)
        report = LevelEvents.extension(ctx.channel.id, members)

        if report:
            await ctx.response.send_message(report)
        else:
            await ctx.response.send_message('Не сработало')


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelsCog(bot))
