from discord.ext import commands
from cogs.fun import FunCog
from cogs.listeners import ListenerCog

cogs = [
    FunCog,
    ListenerCog
]


def register_cogs(client: commands.Bot):
    for cog in cogs:
        client.add_cog(cog(client))
