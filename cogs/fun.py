import discord
import random
from discord import app_commands
from discord.ext import commands
from levels.utils.misc import LevelMisc


name = LevelMisc.name


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='хофик', description='Проверь, сколько в тебе хофика')
    async def hof1k(self, ctx: discord.Interaction):
        await ctx.response.defer()
        await ctx.followup.send(f"Сегодня ты хофик на {random.randint(0, 100)}%!")
        #await ctx.response.send_message(f"Сегодня ты хофик на {random.randint(0, 100)}%!")

    @app_commands.command(name='любовь', description='Проверь любовь этих двоих')
    @app_commands.rename(who='чья', target='к-кому')
    @app_commands.describe(who='Чью любовь проверяешь', target='Любовь к кому/чему проверяешь')
    async def love(self, ctx: discord.Interaction, who: str, target: str):
        await ctx.response.defer()
        await ctx.followup.send(f"Любовь {who} к {target} составляет {random.randint(0, 100)}%!")
        #await ctx.response.send_message(f"Любовь {who} к {target} составляет {random.randint(0, 100)}%!")

    @app_commands.command(name='пидор', description='Найди пидора дня')
    async def pidor(self, ctx: discord.Interaction):
        await ctx.response.defer()
        members = LevelMisc.get_members(ctx.channel)
        await ctx.followup.send(f"Пидор дня обнаружен, и это <@{random.choice(members).id}>!")
        #await ctx.response.send_message(f"Пидор дня обнаружен, и это <@{random.choice(members).id}>!")

    @app_commands.command(name='дрочило', description='Узнай, какой ты дрочило')
    async def droch(self, ctx: discord.Interaction):
        await ctx.response.defer()
        sheet = ['желанный', 'незабываемый', 'мрачный', 'изящный', 'вазелиновый', 'ловкий', 'дерзкий', 'опытный',
                 'знойный',
                 'меланхоличный', 'боевой', 'усердный', 'грациозный', 'ветреный', 'коридорный', 'превосходный',
                 'голландский', 'мохнатый', 'нахальный', 'наглый', 'непревзойдённый', 'алчный', 'игривый',
                 'жизнерадостный',
                 'легкомысленный', 'заводной', 'беззаботный', 'ленивый', 'назойливый', 'душный', 'безрассудный',
                 'ироничный', 'импозантный', 'беспощадный']

        await ctx.followup.send(f"Сегодня ты {random.choice(sheet)} дрочило!")
        #await ctx.response.send_message(f"Сегодня ты {random.choice(sheet)} дрочило!")

    @app_commands.command(name='пнуть', description='дотянись ногой до жеппы своей любимки')
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    async def kick(self, ctx: discord.Interaction):
        await ctx.response.defer()
        members = LevelMisc.get_members(ctx.channel)
        await ctx.followup.send(f'{name(ctx.user)} пинает по жеппе {name(random.choice(members))}! <3')
        #await ctx.response.send_message(f'{name(ctx.user)} пинает по жеппе {name(random.choice(members))}! <3')

    @kick.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.defer()
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(str(error), ephemeral=True)
            #await interaction.response.send_message(str(error), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
