import os
import random
import discord
from discord.ext import commands


def main():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f"{client.user.name} connected.")

    @commands.command(name='хофик')
    async def cmd_hofik(ctx):
        await ctx.message.reply(f"Сегодня ты хофик на {random.randint(0, 100)}%!!!")

    client.add_command(cmd_hofik)
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()
