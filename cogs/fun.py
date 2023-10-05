import discord
import random
from discord import app_commands
from discord.ext import commands
from levels.utils.misc import LevelMisc


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='хофик', description='Проверь, сколько в тебе хофика')
    async def hof1k(self, ctx: discord.Interaction):
        await ctx.response.send_message(f"Сегодня ты хофик на {random.randint(0, 100)}%!")

    @app_commands.command(name='любовь', description='Проверь любовь этих двоих')
    @app_commands.rename(who='чья', target='к-кому')
    @app_commands.describe(who='Чью любовь проверяешь', target='Любовь к кому/чему проверяешь')
    async def love(self, ctx: discord.Interaction, who: str, target: str):
        await ctx.response.send_message(f"Любовь {who} к {target} составляет {random.randint(0, 100)}%!")

    @app_commands.command(name='пидор', description='Найди пидора дня')
    async def pidor(self, ctx: discord.Interaction):
        members = LevelMisc.get_members(ctx.channel)
        await ctx.response.send_message(f"Пидор дня обнаружен, и это <@{random.choice(members).id}>!")

    @app_commands.command(name='дрочило', description='Узнай, какой ты дрочило')
    async def droch(self, ctx: discord.Interaction):
        sheet = ['желанный', 'незабываемый', 'мрачный', 'изящный', 'вазелиновый', 'ловкий', 'дерзкий', 'опытный',
                 'знойный',
                 'меланхоличный', 'боевой', 'усердный', 'грациозный', 'ветреный', 'коридорный', 'превосходный',
                 'голландский', 'мохнатый', 'нахальный', 'наглый', 'непревзойдённый', 'алчный', 'игривый',
                 'жизнерадостный',
                 'легкомысленный', 'заводной', 'беззаботный', 'ленивый', 'назойливый', 'душный', 'безрассудный',
                 'ироничный', 'импозантный', 'беспощадный']

        await ctx.response.send_message(f"Сегодня ты {random.choice(sheet)} дрочило!")


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
