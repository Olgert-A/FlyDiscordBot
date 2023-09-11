import random
import logging
from discord.ext import commands
from levels.db.current import get_db, get_uses_db


def phrase(points):
    phrases = {(-1000, 0): ["Отрицательный? Ты точно мужик?",
                            "Как вообще можно отрастить минусовой член?",
                            "На доске Позор года висит твоя фотография.",
                            "Девочки вкладывают поролон в лифчик, а ты мягкие игрушки в трусы?",
                            "Будь осторожен во время депиляции, можно случайно сорвать зародыш члена."],
               (0, 20): ["Команда исследователей США создали микроскоп, чтобы разглядеть твоё достоинство.",
                    "Возможно, у тебя азиатские корни.",
                    "Натирай три раза в день свой корень, и уже через неделю он окрепнет и вырастет. Или опухнет.",
                    "Маловат, надеюсь, у тебя в жизни есть другой повод для гордости.",
                    "Даже миниатюрная птичка колибри может посоревноваться с этим размером.",
                    "Встречайте, майорд, а затем первый король франков, его величество Пипин Короткий",
                    "Почти все методы увеличения размера являются обманом, но ты можешь отрастить живот, чтобы скрыть этот позор",
                    "Полезно уметь радоваться тому, что есть, но высший пилотаж - радоваться тому, чего нет",
                    "Если бы ты попал в древнюю Грецию, Микеланджело точно бы вдохновился этим размером",
                    "Я знаю три самых лучших инвестиции - Айваза в доллары, Хуббы в Яндекс.Практикум и твоей девушки в курс горлового минета",
                    "Даже если ты не сможешь рассмешить девушку крутой шуткой, у тебя всегда в запасе будет твой размер.",
                    "Понимаю, у тебя был сложный выбор между длинным и тонким, и толстым и коротким.",
                    "Или, как говорят парни, 20-25 см.",
                    "Такой размер пытаются компенсировать рейтингом в онлайн игре, но ты и там не преуспел.",
                    "Когда ты заходишь в общественный туалет, что тебя напрягает больше - что у школьника член в расслабленном состоянии больше, чем твой в стоячем, или что у тебя стоит на школьника?",
                    "Не размер маленький, а ладони большие."],
               (20, 50): ["Неплохо, но можно лучше.",
                          "Ты, кажется, находишься наверху списка ебырей района, но это не точно.",
                          "Продолжай наращивать и скоро сможешь складывать вдвое.",
                          "Середнячок. Не повод для гордости, не причина для грусти.",
                          "Думаешь, это уже достаточно для аутофелляции?",
                          "Почти можно использовать как маятник для настенных часов.",
                          "Сопливый кувалда, Грязный отрыв и другие имена монстров из русской локализации Диабло 2 вполне подошли бы тебе.",
                          "Поздравляю!",
                          "Надеюсь, это не единственное твоё достижение за прошедший год. Или жизнь.",
                          "Похоже, ты много работал руками, чтобы достичь таких результатов."]}

    for (start, end), v in phrases.items():
        if start <= points < end:
            return random.choice(v)

    return ""


def convert_points(points):
    return points / 100.


def random_points():
    return random.randint(-6, 10)


@commands.command(name='лвл-рег')
async def cmd_levels_reg(ctx):
    get_db().channel_reg(ctx.channel.id)
    for m in ctx.channel.members:
        if not m.bot:
            get_db().points_add(ctx.channel.id, m.id, 0)
            get_uses_db().update(ctx.channel.id, m.id, 0)

    await ctx.message.delete()
    await ctx.channel.send(f"""Канал зарегистрирован в программе **Ебырьметр**! Каждое сообщение пользователя может как повысить, так и понизить уровень. 
    !ебырь - вывод твоего уровня 
    !ебыри - таблица уровней""")


@commands.command(name='лвл-стоп')
async def cmd_levels_stop(ctx):
    get_db().channel_unreg(ctx.channel.id)
    await ctx.message.delete()
    await ctx.channel.send(f"Канал больше не участвует в программе **Ебырьметр**")


@commands.command(name='ебырь')
async def cmd_levels_points(ctx):
    if not (points := get_db().points_get(ctx.channel.id, ctx.author.id)):
        await ctx.message.reply(f"Sasi <:pepe_loh:1022083481725063238>")
        return

    points = convert_points(points)
    await ctx.message.reply(f"У тебя {points} см. " + phrase(points))


@commands.command(name='ебыри')
async def cmd_levels_table(ctx):
    def name(member):
        if member.nick:
            return member.nick
        elif member.global_name:
            return member.global_name
        else:
            return member.name

    members = {m.id: name(m) for m in ctx.channel.members if not m.bot}
    table = get_db().points_table(ctx.channel.id)

    if not table:
        await ctx.message.reply(f"Sasi <:pepe_loh:1022083481725063238>")
        return

    table = sorted(table.items(), key=lambda v: v[1], reverse=True)

    points = [f"{i}. {name}: {convert_points(v)} см."
              for i, (p, v) in enumerate(table)
              if (name := members.get(p))]
    await ctx.message.reply('\n'.join(points))


@commands.command(name='выебать')
async def cmd_levels_kick(ctx, target=None):
    uses = get_uses_db().get(ctx.channel.id, ctx.author.id)

    if uses and uses >= 5:
        await ctx.message.reply("Ты уже выебал 5 раз сегодня, с тебя хватит!")
        return

    def get_target_id():
        members = [m for m in ctx.channel.members if not m.bot]
        if target:
            # if m.id in target return m.id else return None
            for m in members:
                if str(m.id) in target:
                    return m.id
        else:
            return random.choice(members).id

    def get_points(member_id):
        return get_db().points_get(ctx.channel.id, member_id)

    if not (target_id := get_target_id()):
        await ctx.message.reply("Тегни цель, еблан")
        return

    author_pts = get_points(ctx.author.id)
    target_pts = get_points(target_id)
    pts = random.randint(0, abs(author_pts - target_pts))
    chance = random.randint(-author_pts, target_pts) / max([author_pts, target_pts])
    pts_up = int(pts * chance)

    get_db().points_add(ctx.channel.id, ctx.author.id, pts_up)
    get_db().points_add(ctx.channel.id, target_id, -pts_up)
    get_uses_db().update(ctx.channel.id, ctx.author.id, 1)
    await ctx.message.reply(f"Ты подкрадываешься к <@{target_id}> и делаешь {random.randint(1, 10)} фрикций, "
                            f"{'получив' if pts_up >= 0 else 'потеряв'} {convert_points(pts_up):.2f} см.")

