import discord
import random
from discord import app_commands
from discord.ext import commands
from db.current import get_rolls_db
from levels.utils.misc import LevelMisc


name = LevelMisc.name


def check_bot_author_permission():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 776537982924619786

    return app_commands.check(predicate)


class RollsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='лудоманить',
                          description='Административная команда для подключения сервера к рулетке сердечек')
    @check_bot_author_permission()
    async def rolls_reg(self, ctx: discord.Interaction):
        get_rolls_db().guild_reg(ctx.guild.id)
        for m in ctx.guild.members:
            get_rolls_db().points_add(ctx.guild.id, m.id, 0)

        await ctx.response.send_message(f'Канал зарегистрирован в программе **Сердечки**!', ephemeral=True)

    @app_commands.command(name='расстаться',
                          description='Административная команда для отключения сервера от рулетки сердечек')
    @check_bot_author_permission()
    async def rolls_reg_stop(self, ctx: discord.Interaction):
        get_rolls_db().guild_reg_stop(ctx.guild.id)

        await ctx.response.send_message(f'Канал отписан от программы **Сердечки**!', ephemeral=True)

    @app_commands.command(name='крутить',
                          description='Рулетка сердечек')
    @app_commands.rename(roll_pts='сердечки')
    @app_commands.describe(roll_pts='Сколько крутим')
    @app_commands.checks.cooldown(1, 60)
    async def roll(self, ctx: discord.Interaction, roll_pts: int):
        if roll_pts < 0:
            await ctx.response.send_message(f"Низя крутить, когда твои сердечки кончились")
            return
        
        user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
        if roll_pts > user_pts:
            await ctx.response.send_message(f"У тебя маловато сердечек на счету, дружок")
            return

        win_sign = random.choice([1, -1])
        pts_to_add = win_sign * roll_pts
        get_rolls_db().points_add(ctx.guild.id, ctx.user.id, pts_to_add)
        await ctx.response.send_message(f"{name(ctx.user)} ставит {roll_pts} и {'выигрывает' if win_sign == 1 else 'проигрывает'}! Теперь на счету сердечек: {user_pts + pts_to_add}.")

    @app_commands.command(name='сердечки',
                          description='Узнай, сколько у тебя сердечек')
    async def points(self, ctx: discord.Interaction):
        user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
        await ctx.response.send_message(f"{name(ctx.user)}, у тебя на счету сердечек: {user_pts}.")

    @roll.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RollsCog(bot))
