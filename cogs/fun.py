import discord
import random
from discord import app_commands
from discord.ext import commands


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
