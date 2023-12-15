import discord
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

    @app_commands.command(name='крутить')
    @app_commands.rename(roll_pts='сердечки')
    @app_commands.describe(who='Сколько крутим')
    async def roll(self, ctx: discord.Interaction, roll_pts: int):
        if(roll_pts < 0)
            await ctx.response.send_message(f"Низя крутить, когда твои сердечки кончились")
            return
        
        user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
        if(roll_pts > user_pts)
            await ctx.response.send_message(f"У тебя маловато сердечек на счету, дружок")
            return

        win_sign = random.choice([1, -1])
        pts_to_add = win_sign * roll_pts
        get_rolls_db().points_add(ctx.guild.id, ctx.user.id, pts_to_add)
        await ctx.response.send_message(f"{name(ctx.user)} ставит {roll_pts} и {'выигрывает' if win_sign else 'проигрывает'}! Теперь на счету {user_pts + pts_to_add} сердечек."

    @app_commands.command(name='сердечки')
    async def points(self, ctx: discord.Interaction):
        user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
        await ctx.response.send_message(f"{name(ctx.user)}, у тебя на счету {user_pts} сердечек."
        
          


async def setup(bot: commands.Bot):
    await bot.add_cog(RollsCog(bot))
