import logging
import datetime
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
        # contract dictionary
        # key - message_id: int
        # value - tuple(user_id: int, target_id: int, points: int, timestamp: datetime)
        self.duels = {}

    def duels_add(self, message_id, user_id, target_id, points, timestamp):
        logging.info(f'add contract: {message_id}--{user_id}--{target_id}--{points}--{timestamp}')
        self.duels[message_id] = (user_id, target_id, points, timestamp)
        logging.info(f'contracts: {self.duels}')

    def duels_get_by_id(self, message_id):
        logging.info(f'get contract: {message_id}')
        logging.info(f'contracts: {self.duels}')
        return self.duels.get(message_id)

    def is_contract_exist(self, user_id_to_find, target_id_to_find):
        logging.info(f'is contract exist: {user_id_to_find}--{target_id_to_find}')
        for message_id, (user_id, target_id, points, timestamp) in self.duels:
            if user_id_to_find == user_id and target_id_to_find == target_id:
                logging.info(f'True')
                return True

        logging.info(f'False')
        return False

    def duel_clear(self, message_id):
        if self.duels.get(message_id):
            logging.info(f'delete contract: {message_id}')
            del self.duels[message_id]
            logging.info(f'contracts: {self.duels}')

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
            await ctx.response.send_message(f"Низя крутить меньше 0 сердечек")
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

    @staticmethod
    def check_points_exist(guild_id, user_id, points):
        user_points = get_rolls_db().points_get(guild_id, user_id)
        return user_points >= points

    @app_commands.command(name='test1')
    async def test(self, ctx: discord.Interaction):
        get_rolls_db().duels_contract_add(123456789012345, datetime.datetime.now())
        get_rolls_db().duel_get()

    @app_commands.command(name='дуэль',
                          description='Укради чужие сердечки')
    @app_commands.rename(target='цель')
    @app_commands.describe(target='С кем деремся за сердечки')
    @app_commands.rename(points='ставка')
    @app_commands.describe(points='Сколько сердечек хотим украсть')
    @app_commands.checks.cooldown(1, 60)
    async def duel(self, ctx: discord.Interaction, target: discord.Member, points: int):
        user = ctx.user

        user_points_check = self.check_points_exist(ctx.guild.id, user.id, points)
        target_points_check = self.check_points_exist(ctx.guild.id, target.id, points)

        if points < 0:
            await ctx.response.send_message(f"Низя крутить меньше 0 сердечек")
            return

        if not user_points_check:
            await ctx.response.send_message(f"У тебя маловато сердечек на счету, дружок")
            return

        if not target_points_check:
            await ctx.response.send_message(f"У твоей цели нету столько сердечек, дружок")
            return

        contract = self.is_contract_exist(user.id, target.id)
        if contract:
            await ctx.response.send_message(f"Ты уже ждёшь дуэли со своей целью")
            return

        await ctx.response.send_message(
            f"<@{target.id}>, с тобой хочет сразить {name(user)} за твои сердечки. Ставка дуэли {points}. Жми реакцию, чтобы согласиться или отказаться")
        message = await ctx.original_response()
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')
        logging.info(f'{message.id} - {datetime.datetime.now()} - {user.id} - {target.id} - {points}')
        self.duels_add(message.id, user.id, target.id, points, datetime.datetime.now())

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        message = reaction.message
        logging.info(f'message: {message.id}')
        #get_rolls_db().duel_get()
        contract = self.duels_get_by_id(message.id)
        logging.info(f'contract: {contract}')

        if not contract:
            return

        user_id, target_id, points, timestamp = contract

        if target_id != user.id:
            return

        user_points_check = self.check_points_exist(message.guild.id, user_id, points)
        target_points_check = self.check_points_exist(message.guild.id, target_id, points)

        if not user_points_check or not target_points_check:
            await message.channel.send(f'<@{user_id}>, <@{target_id}>, у кого-то из вас нету нужного количества сердечек, дуэль отменена!')
            self.duel_clear(message.id)

        win_sign = random.choice([1, -1])
        pts_to_add = win_sign * points
        get_rolls_db().points_add(message.guild.id, user_id, pts_to_add)
        get_rolls_db().points_add(message.guild.id, target_id, -pts_to_add)
        self.duel_clear(message.id)
        await message.channel.send(f"<@{user_id}> вызывает на дуэль <@{target_id}> и {'выигрывает' if win_sign == 1 else 'проигрывает'} {points} сердечек!")

    @roll.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RollsCog(bot))
