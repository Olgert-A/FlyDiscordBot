import logging
import datetime
import discord
import random
import asyncio
from discord import app_commands
from discord.ext import commands
from db.current import get_rolls_db
from levels.utils.misc import LevelMisc
from rolls.utils.roll import RollParser, RollTypes


name = LevelMisc.name


def check_bot_author_permission():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 776537982924619786

    return app_commands.check(predicate)

def check_server_id_permission():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.guild.id == 780923811264200754

    return app_commands.check(predicate)

def check_channel_id_permission():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.channel.id == 822903067233878016

    return app_commands.check(predicate)

roll_cooldown = app_commands.checks.Cooldown(1, 60)
duel_cooldown = app_commands.checks.Cooldown(1, 60)


def roll_cooldown_checker(interaction: discord.Interaction):
    return roll_cooldown

def duel_cooldown_checker(interaction: discord.Interaction):
    return duel_cooldown


class RollsCog(commands.Cog):    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # contract dictionary
        # key - message_id: int
        # value - tuple(user_id: int, target_id: int, points: int, timestamp: datetime)
        self.duels = {}
        self.random_factor = [-1, -1, -1, 1, 1, 1]
        self.factor_index = 6
        self.huesos_factor  = [-1, -1, 1, 1, 1, 1]
        self.huesos_index = 6
        self.group_roll_user_win_pts = []
        self.group_roll_users = []
        self.group_roll_factor = [1, 1, 1, 1, 1, 1, 1, 1, 1, -1]
        self.group_roll_index = -1
        self.roulette_task: asyncio.Task = None
        self.mine_users = []
        self.mine_factor = [-1, -1, -0.5, -0.5, 0, 0, 0.25, 0.25, 0.5, 1]
        self.mine_shots = set()
        self.mine_roll_task: asyncio.Task = None
        self.risk_chances = [(90, 2), (80, 3), (70, 4), (60, 5), (50, 6)]
        self.risk_users: dict[int, int] = {}
        self.risk_tasks: dict[int, asyncio.Task | None] = {}

    async def finish_user_risk_streak(self, user_id: int):
        try:
            # Ожидание 1 час (3600 секунд)
            await asyncio.sleep(3600)

            current_task = asyncio.current_task()
            task = self.risk_tasks.get(user_id)
            if task:
                if task != current_task:
                    return

                self.risk_users[user_id] = -1
                self.risk_tasks[user_id] = None

        except asyncio.CancelledError:
            # Сюда код заходит, когда мы делаем self.roulette_task.cancel() при новом вызове команды.
            # Просто игнорируем, позволяя задаче тихо перезапуститься.
            pass
    
    @app_commands.command(name='канал', description='Узнать id канала')
    @check_bot_author_permission()
    async def get_setver_id(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True) # ephemeral=True, чтобы ответ видел только автор
    
        try:
            # Преобразуем ID из строки в число
            id_num = 822903067233878016
            
            # 2. Ищем канал (сначла в кэше, если нет — через API)
            channel = self.bot.get_channel(id_num) or await self.bot.fetch_channel(id_num)
            
            # 3. Отправляем сообщение в тот самый закрытый канал
            await channel.send(f"Сообщение из слэш-команды от {ctx.user.mention}")
            
            # 4. Отвечаем пользователю, который вызвал команду
            await ctx.followup.send(f"✅ Успешно отправлено в канал {channel.mention}!")
            
        except ValueError:
            await ctx.followup.send("❌ Неверный формат ID. Введите только цифры.")
        except discord.Forbidden:
            await ctx.followup.send("❌ У бота нет доступа (права View Channel) к этому каналу.")
        except discord.NotFound:
            await ctx.followup.send("❌ Канал с таким ID не найден.")
        except Exception as e:
            await ctx.followup.send(f"❌ Произошла ошибка: {e}")
        

    @app_commands.command(name='pointsupd', description='обновление размера хранения сердечек')
    @check_bot_author_permission()
    async def update_points_type(self, ctx: discord.Interaction):
        await ctx.response.defer()
        get_rolls_db().duels_points_update()
        get_rolls_db().rolls_points_update()
        await ctx.followup.send("Обновлено до BIGINT")
        
        
    @app_commands.command(name='риск', description='All in. С каждой круткой шанс ниже, выигрыш больше')
    @check_server_id_permission()
    async def risk(self, ctx: discord.Interaction):
        try:
            await ctx.response.defer()

            if ctx.user.id not in self.risk_users:
                self.risk_users[ctx.user.id] = -1
    
            if ctx.user.id not in self.risk_tasks:
                self.risk_tasks[ctx.user.id] = None 
    
            user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
    
            if self.risk_tasks[ctx.user.id] and not self.risk_tasks[ctx.user.id].done():
                self.risk_tasks[ctx.user.id].cancel()  # 2. Отменяем задачу
                
            # 3. Очищаем переменную в любом случае (даже если задача была завершена)
            self.risk_tasks[ctx.user.id] = None
    
            if user_pts == 0:
                self.risk_users[ctx.user.id] = -1
                await ctx.followup.send("Ты не можешь ставить 0 сердечек. Твои шансы сброшены на первоначальные. Попробуй, когда накопишь больше 0.")
                return
    
            current_user_risk_index = self.risk_users[ctx.user.id]
            if current_user_risk_index < len(self.risk_chances) - 1:
                current_user_risk_index += 1
                self.risk_users[ctx.user.id] = current_user_risk_index
    
            chance, win_koef = self.risk_chances[current_user_risk_index]
            chance = chance // 10
            risk_win_condition = [1] * chance
            risk_win_condition.extend([-1] * (10 - chance))
            random.shuffle(risk_win_condition)
            win_sign = risk_win_condition[0]
            
            pts_to_add = int(win_sign * user_pts * win_koef) - user_pts if win_sign > 0 else -user_pts
            get_rolls_db().points_add(ctx.guild.id, ctx.user.id, pts_to_add)
            result = f"{name(ctx.user)} поставил {user_pts} сердечек с шансом {chance * 10}%, коэффициентом {win_koef}"
            if win_sign > 0:
                result += f" и выиграл {pts_to_add} сердечек!"
                self.risk_tasks[ctx.user.id] = asyncio.create_task(self.finish_user_risk_streak(ctx.user.id))    
            else:
                result += f" и проиграл все {user_pts} сердечек!"
                self.risk_users[ctx.user.id] = -1
    
            await ctx.followup.send(result)

        except Exception as e: # Если произошла ЛЮБАЯ ошибка, бот напишет её в чат
            import traceback
            error_message = f"❌ Произошла ошибка в коде:\n```python\n{traceback.format_exc()}\n```"
            await ctx.followup.send(error_message)
            
        
    

    async def finish_mine_roll(self, guild_id: int, channel: discord.abc.Messageable):
        try:
            # Ожидание 1 час (3600 секунд)
            await asyncio.sleep(1200)

            current_task = asyncio.current_task()
            if self.mine_roll_task != current_task:
                return

            result = "Раунд казика завершён. Поля ставок перемешаны."
                            
            self.mine_users.clear()
            self.mine_shots.clear()
            self.mine_roll_task = None

            # Отправляем сообщение в канал завершившейся рулетки
            await channel.send(result)

        except asyncio.CancelledError:
            # Сюда код заходит, когда мы делаем self.roulette_task.cancel() при новом вызове команды.
            # Просто игнорируем, позволяя задаче тихо перезапуститься.
            pass
  
    @app_commands.command(name='казик', description='Просто поставь на поле')
    @app_commands.rename(mine_position='номер-поля')
    @app_commands.describe(mine_position='Выбери поле от 0 до 9 для all in')
    @check_server_id_permission()
    async def miner_roll(self, ctx: discord.Interaction, mine_position: int):
        try:
            await ctx.response.defer()
        
            current_user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
    
            if any(user_id == ctx.user.id for user_id in self.mine_users):
                await ctx.followup.send("Ты уже делал ставку в этом казике! Ожидай перезапуск.")
                return
    
            if current_user_pts == 0:
                await ctx.followup.send("У тебя нет сердечек, чтобы участвовать в казике. Лох")
                return
            
            if mine_position < 0 or mine_position >= len(self.mine_factor):
                result = f"Номер поля должен быть от 0 до {len(self.mine_factor) - 1}"
                if len(self.mine_shots) > 0:
                    result += f" Проверенные поля: {', '.join([str(n) for n in self.mine_shots])}"
                await ctx.followup.send(result)
                return 
    
            if mine_position in self.mine_shots:
                await ctx.followup.send(f"Данное поле уже проверено. Проверенные поля: {', '.join([str(n) for n in self.mine_shots])}")
                return
    
            if len(self.mine_users) == 0:
                random.shuffle(self.mine_factor)
            
            self.mine_shots.add(mine_position)
            
            koef = self.mine_factor[mine_position]
            points_to_add = int(koef * current_user_pts)
            self.mine_users.append(ctx.user.id)
            get_rolls_db().points_add(ctx.guild.id, ctx.user.id, points_to_add) 

            result = f"{name(ctx.user)} поставил {current_user_pts} сердечек на поле {mine_position} с коэффициентом {int(100*koef)}% и "
            if koef > 0:
                result += f"выигрывает {points_to_add} сердечек."
            elif koef < 0:
                result += f"проигрывает {-points_to_add} сердечек."
            else:
                result += f"попадает на коэффициент 0, ничего не получая. Ебать сосал, конечно."
            
            if len(self.mine_users) == len(self.mine_factor):
                result += " Все поля открыты. Раунд казика завершен."
                self.mine_users.clear()
                self.mine_shots.clear()
                if self.mine_roll_task and not self.mine_roll_task.done():
                    self.mine_roll_task.cancel() 

                self.mine_roll_task = None
            elif len(self.mine_users) == 1:
                result += " Раунд автоматически закончится через 20 минут."
                self.mine_roll_task = asyncio.create_task(self.finish_mine_roll(ctx.guild.id, ctx.channel))

            await ctx.followup.send(result)
            
        except Exception as e: # Если произошла ЛЮБАЯ ошибка, бот напишет её в чат
            import traceback
            error_message = f"❌ Произошла ошибка в коде:\n```python\n{traceback.format_exc()}\n```"
            await ctx.followup.send(error_message)
    
    def get_win_sign(self):
        self.factor_index += 1
        if self.factor_index >= len(self.random_factor):
            self.factor_index = 0
            random.shuffle(self.random_factor)
            
        return self.random_factor[self.factor_index]

    def get_huesos_sign(self):
        self.huesos_index += 1
        if self.huesos_index >= len(self.huesos_factor):
            self.huesos_index = 0
            random.shuffle(self.huesos_factor)
            
        return self.huesos_factor[self.huesos_index]      

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
        for message_id, (user_id, target_id, points, timestamp) in self.duels.items():
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
        await ctx.response.defer()
        get_rolls_db().guild_reg(ctx.guild.id)
        for m in ctx.guild.members:
            get_rolls_db().points_add(ctx.guild.id, m.id, 0)

        await ctx.followup.send(f'Сервер зарегистрирован в программе **Сердечки**!', ephemeral=True)

    @app_commands.command(name='расстаться',
                          description='Административная команда для отключения сервера от рулетки сердечек')
    @check_bot_author_permission()
    async def rolls_reg_stop(self, ctx: discord.Interaction):
        await ctx.response.defer()
        get_rolls_db().guild_reg_stop(ctx.guild.id)
        await ctx.followup.send(f'Канал отписан от программы **Сердечки**!', ephemeral=True)

    @app_commands.command(name='test1')
    async def test1(self, ctx: discord.Interaction, time: int):
        get_rolls_db().duels_contract_add(2, 2, 2, 2, datetime.datetime.now() - datetime.timedelta(minutes=6))
        get_rolls_db().duels_contract_add(2, 2, 2, 2, datetime.datetime.now() - datetime.timedelta(minutes=2))
        get_rolls_db().duel_clear_older_than(datetime.datetime.now() - datetime.timedelta(minutes=time))
        get_rolls_db().duel_get()

    @app_commands.command(name='одарить', description='Административная команда для выдачи сердечек')
    @app_commands.rename(target='цель')
    @app_commands.describe(target='Кому выдать сердечки')
    @app_commands.rename(points='количество')
    @app_commands.describe(points='Сколько сердечек выдать')
    @check_bot_author_permission()
    async def give_hearts(self, ctx: discord.Interaction, target: discord.Member, points: int):
        await ctx.response.defer()
        get_rolls_db().points_add(ctx.guild.id, target.id, points)
        await ctx.followup.send(f'{name(target)} получает сердечки в количестве {points}!')

    @app_commands.command(name='я_хуесос', description='Рулетка всех сердечек с повышенным шансом выигрыша')
    @check_server_id_permission()
    async def huesos_roll(self, ctx: discord.Interaction):
        try:
            await ctx.response.defer()
            user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
            win_sign = self.get_huesos_sign()
            pts_to_add = win_sign * user_pts
            get_rolls_db().points_add(ctx.guild.id, ctx.user.id, pts_to_add)
            win_texts = ["пожал плоды своей искренности", "на этот раз остался в плюсе", "cорвал баснословный куш для нищих", "достиг головокружительного успеха", "доказал, что если долго пресмыкаться, система выплюнет тебе кость", "выиграл ровно столько, чтобы на секунду забыть, какое он ничтожество", "облизал барский сапог, выпросив-таки свою подачку"]
            lose_texts = ["позорно проебал", "доказал это очередным проигрышем", "остался попёрдывать лежа в канаве", "пустил свою жопу по миру", "продемонстрировал эталонный пример тотальной никчёмности", "остался смаковать привкус собственного поражения"]
            random.shuffle(win_texts)
            random.shuffle(lose_texts)      
            await ctx.followup.send(f"{name(ctx.user)} признался в том, что он хуесос и {win_texts[0] if win_sign == 1 else lose_texts[0]}! Теперь на счету сердечек: {user_pts + pts_to_add}!")
        except Exception as e: # Если произошла ЛЮБАЯ ошибка, бот напишет её в чат
            import traceback
            error_message = f"❌ Произошла ошибка в коде:\n```python\n{traceback.format_exc()}\n```"
            await ctx.followup.send(error_message)

    def cancel_roulette_task(self):
        # 1. Проверяем, что задача существует и ещё выполняется
        if self.roulette_task and not self.roulette_task.done():
            self.roulette_task.cancel()  # 2. Отменяем задачу
            
        # 3. Очищаем переменную в любом случае (даже если задача была завершена)
        self.roulette_task = None


    async def cog_load(self):
        logging.info("cog load")
        asyncio.create_task(self.check_db_on_startup())

    async def check_db_on_startup(self):
        await self.bot.wait_until_ready()
        try:
            # Получаем текущий список участников из базы
            grouproll_users = get_rolls_db().grouproll_get_users()
            
            # Если в базе кто-то есть, значит бот упал или перезапустился во время таймера
            if len(grouproll_users) > 0:
                self.roulette_task = asyncio.create_task(self.finish_group_roll())
                    
        except Exception as e:
            logging.info(f"[Ошибка] Не удалось возобновить штурвал при старте: {e}")
    
    async def finish_group_roll(self):
        try:
            await asyncio.sleep(1200)
            current_task = asyncio.current_task()
            if self.roulette_task != current_task:
                return

            self.roulette_task = None

            grouproll_users = get_rolls_db().grouproll_get_users()
            if len(grouproll_users) == 0:
                return

            for _id, user_id, points in grouproll_users:
                logging.info(f"user={user_id} points={points}")

            guild_id = 780923811264200754
            channel_id = 822903067233878016
            
            guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            
            winner_choice = random.choice(grouproll_users)
            winner_id = winner_choice[1]
            win_points = sum(points for _id, user_id, points in grouproll_users)
            winner = guild.get_member(winner_id) or await guild.fetch_member(winner_id)
            get_rolls_db().points_add(780923811264200754, winner_id, win_points)
            get_rolls_db().clear_grouproll()
            if channel:
                await channel.send(f"""Голландский штурвал завершён безоговорочной победой {name(winner)}!""")
              
        except asyncio.CancelledError:
            # Сюда код заходит, когда мы делаем self.roulette_task.cancel() при новом вызове команды.
            # Просто игнорируем, позволяя задаче тихо перезапуститься.
            pass
    
    @app_commands.command(name='голландский_штурвал', description='Групповая рулетка всех сердечек')
    @check_server_id_permission()
    @check_channel_id_permission()
    async def group_roll(self, ctx: discord.Interaction):
        await ctx.response.defer()

        try: # Начало безопасного блока
            group_roll_users = get_rolls_db().grouproll_get_users()

            for _id, user_id, points in group_roll_users:
                if ctx.user.id == user_id:
                    await ctx.followup.send(f"Ты уже участвуешь в голландском штурвале со своими {points} сердечками!")
                    return

            user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)

            if user_pts <= 0:
                await ctx.followup.send("У тебя слишком маленький ||счёт сердечек|| для участия в групповом штурвале.")
                return

            if self.roulette_task and not self.roulette_task.done():
                self.roulette_task.cancel() 
            
            self.roulette_task = None

            get_rolls_db().grouproll_add_user(ctx.user.id, user_pts)
            get_rolls_db().points_add(ctx.guild.id, ctx.user.id, -user_pts)
            self.roulette_task = asyncio.create_task(self.finish_group_roll())

            result = f"{name(ctx.user)} присоединился к голландскому штурвалу со своими {user_pts} сердечками. Участники: "
            
            grouproll_users = get_rolls_db().grouproll_get_users()
            grouproll_members = []
            
            for _id, user_id, points in grouproll_users:
                member = ctx.guild.get_member(user_id) or await ctx.guild.fetch_member(user_id)
                if member:
                    grouproll_members.append(member)

            result += ", ".join(name(member) for member in grouproll_members)
            result += ". Розыгрыш через 20 минут."
            
            await ctx.followup.send(result)
                       
        except Exception as e: # Если произошла ЛЮБАЯ ошибка, бот напишет её в чат
            import traceback
            error_message = f"❌ Произошла ошибка в коде:\n```python\n{traceback.format_exc()}\n```"
            await ctx.followup.send(error_message)

    
    
    @app_commands.command(name='крутить',
                          description='Рулетка сердечек')
    @app_commands.rename(pts_arg='сердечки')
    @app_commands.describe(pts_arg='Сколько крутим')
    async def roll(self, ctx: discord.Interaction, pts_arg: str = "100%"):
        try:
            await ctx.response.defer()
            parsed_pts = RollParser.parse(pts_arg)
            if not parsed_pts:
                await ctx.followup.send(f"Укажи либо **all**, либо процент сердечек (например **50%**), либо четкое количество, которое хочешь крутить, дружок")
                #app_commands.Cooldown.reset(roll_cooldown)
                return
    
            user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
    
            factor, roll_type = parsed_pts
            logging.info(parsed_pts)
    
            if roll_type == RollTypes.POINTS:
                roll_pts = factor
    
            if roll_type == RollTypes.PERCENT:
                roll_pts = int(user_pts * factor)
    
            if roll_type == RollTypes.ALL:
                roll_pts = user_pts
    
            if roll_pts > user_pts or user_pts <= 0:
                await ctx.followup.send(f"У тебя маловато сердечек на счету, дружок")
                #app_commands.Cooldown.reset(roll_cooldown)
                return
    
            #win_sign = #random.choice([2, 1, -1])
            win_sign = self.get_win_sign() #1 if win_sign > 0 else -1
            pts_to_add = win_sign * roll_pts
            get_rolls_db().points_add(ctx.guild.id, ctx.user.id, pts_to_add)
            await ctx.followup.send(f"{name(ctx.user)} ставит {roll_pts} и {'выигрывает' if win_sign == 1 else 'проигрывает'}! Теперь на счету сердечек: {user_pts + pts_to_add}!")
        except Exception as e: # Если произошла ЛЮБАЯ ошибка, бот напишет её в чат
            import traceback
            error_message = f"❌ Произошла ошибка в коде:\n```python\n{traceback.format_exc()}\n```"
            await ctx.followup.send(error_message)

    @app_commands.command(name='сердечки',
                          description='Узнай, сколько у тебя сердечек')
    async def points(self, ctx: discord.Interaction):
        await ctx.response.defer()
        user_pts = get_rolls_db().points_get(ctx.guild.id, ctx.user.id)
        await ctx.followup.send(f"{name(ctx.user)}, у тебя на счету сердечек: {user_pts}.")

    @staticmethod
    def check_points_exist(guild_id, user_id, points):
        user_points = get_rolls_db().points_get(guild_id, user_id)
        return user_points >= points

    @app_commands.command(name='сброс',
                          description='Административная команда для сброса активных контрактов дуэлей')
    @check_bot_author_permission()
    async def reset_contracts(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        get_rolls_db().duel_clear_older_than(datetime.datetime.now())
        await ctx.followup.send(f"Контракты очищены!")
            
    @app_commands.command(name='дуэль',
                          description='Укради чужие сердечки')
    @app_commands.rename(target='цель')
    @app_commands.describe(target='С кем деремся за сердечки')
    @app_commands.rename(points='ставка')
    @app_commands.describe(points='Сколько сердечек хотим украсть')
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    async def duel(self, ctx: discord.Interaction, target: discord.Member, points: int):
        try:
            await ctx.response.defer()
            user = ctx.user
    
            user_points_check = self.check_points_exist(ctx.guild.id, user.id, points)
            target_points_check = self.check_points_exist(ctx.guild.id, target.id, points)
    
            if points < 0:
                await ctx.followup.send(f"Низя крутить меньше 0 сердечек")
                #app_commands.Cooldown.reset(duel_cooldown)
                return
    
            if not user_points_check:
                await ctx.followup.send(f"У тебя маловато сердечек на счету, дружок")
                #app_commands.Cooldown.reset(duel_cooldown)
                return
    
            if not target_points_check:
                await ctx.followup.send(f"У твоей цели нету столько сердечек, дружок")
                #app_commands.Cooldown.reset(duel_cooldown)
                return
    
            contract = self.is_contract_exist(user.id, target.id)
            contract = get_rolls_db().duels_contract_find(user.id, target.id)
            if contract:
                await ctx.followup.send(f'Ты уже ждёшь дуэли со своей целью, дружок')
                #app_commands.Cooldown.reset(duel_cooldown)
                return
    
            await ctx.followup.send(f"<@{target.id}>, с тобой хочет сразиться {name(user)} за твои сердечки. Ставка дуэли {points}. Жми реакцию, чтобы согласиться или отказаться")
            message = await ctx.original_response()
            await message.add_reaction('\N{THUMBS UP SIGN}')
            await message.add_reaction('\N{THUMBS DOWN SIGN}')
            logging.info(f'{message.id} - {datetime.datetime.now()} - {user.id} - {target.id} - {points}')
            self.duels_add(message.id, user.id, target.id, points, datetime.datetime.now())
            get_rolls_db().duels_contract_add(message.id, user.id, target.id, points, datetime.datetime.now())
        except Exception as e: # Если произошла ЛЮБАЯ ошибка, бот напишет её в чат
            import traceback
            error_message = f"❌ Произошла ошибка в коде:\n```python\n{traceback.format_exc()}\n```"
            await ctx.followup.send(error_message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        message = reaction.message
        emoji_yes = '👍'
        emoji_no = '👎'
        logging.info(f'message: {message.id} reaction: {reaction.emoji} eq: {reaction.emoji == emoji_yes}')
        contract = self.duels_get_by_id(message.id)
        contract = get_rolls_db().duels_contract_get(message.id)
        logging.info(f'contract: {contract}')

        if not contract:
            return

        user_id, target_id, points, timestamp = contract

        if target_id != user.id:
            return

        if reaction.emoji == emoji_no:
            await message.channel.send(f'<@{user_id}>, <@{target_id}>, отказался от дуэли, дуэль отменена!')
            self.duel_clear(message.id)
            get_rolls_db().duels_contract_clear(message.id)
            return

        if reaction.emoji == emoji_yes:
            user_points_check = self.check_points_exist(message.guild.id, user_id, points)
            target_points_check = self.check_points_exist(message.guild.id, target_id, points)

            if not user_points_check or not target_points_check:
                await message.channel.send(f'<@{user_id}>, <@{target_id}>, у кого-то из вас нету нужного количества сердечек, дуэль отменена!')
                self.duel_clear(message.id)
                get_rolls_db().duels_contract_clear(message.id)
                return

            win_sign = self.get_win_sign() #random.choice([1, -1])
            pts_to_add = win_sign * points
            get_rolls_db().points_add(message.guild.id, user_id, pts_to_add)
            get_rolls_db().points_add(message.guild.id, target_id, -pts_to_add)
            self.duel_clear(message.id)
            get_rolls_db().duels_contract_clear(message.id)
            await message.channel.send(f"<@{user_id}> вызывает на дуэль <@{target_id}> и {'выигрывает' if win_sign == 1 else 'проигрывает'} {points} сердечек!")

    @roll.error
    @duel.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.defer()
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(str(error), ephemeral=True)
            #await interaction.response.send_message(str(error), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RollsCog(bot))
