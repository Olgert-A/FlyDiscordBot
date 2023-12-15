from discord.ext import commands


async def register_cogs(bot: commands.Bot):
    cogs = ['cogs.fun', 'cogs.listeners', 'cogs.levels', 'cogs.rolls']
    for cog in cogs:
        await bot.load_extension(cog)
