import random
from discord.ext import commands


@commands.command(name='хофик')
async def cmd_hofik(ctx):
    await ctx.message.reply(f"Сегодня ты хофик на {random.randint(0, 100)}%!")


@commands.command(name='пидор')
async def cmd_pidor(ctx):
    members = [m for m in ctx.message.channel.members if not m.bot]
    await ctx.message.reply(f"Пидор дня обнаружен, и это <@{random.choice(members).id}>!")


@commands.command(name='дрочило')
async def cmd_droch(ctx):
    sheet = ['желанный', 'незабываемый', 'мрачный', 'изящный', 'вазелиновый', 'ловкий', 'дерзкий', 'опытный', 'знойный',
             'меланхоличный', 'боевой', 'усердный', 'грациозный', 'ветреный', 'коридорный', 'превосходный',
             'голландский', 'мохнатый', 'нахальный', 'наглый', 'непревзойдённый', 'алчный', 'игривый', 'жизнерадостный',
             'легкомысленный', 'заводной', 'беззаботный', 'ленивый', 'назойливый', 'душный', 'безрассудный',
             'ироничный', 'импозантный', 'беспощадный']

    await ctx.message.reply(f"Сегодня ты {random.choice(sheet)} дрочило!")
