import random
from discord.ext import commands
from levels.db import LevelsDB


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
               (20, 30): ["Неплохо, но можно лучше.",
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


def convert_points(points):
    return points / 20.


def random_points():
    return random.randint(-10, 10)


@commands.command(name='лвл_рег')
async def cmd_levels_reg(ctx):
    LevelsDB().channel_reg(ctx.channel.id)
    for m in ctx.channel.members:
        if not m.bot:
            LevelsDB().points_add(ctx.channel.id, m.id, random_points())

    await ctx.message.delete()
    await ctx.channel.send(f"""Канал зарегистрирован в программе **Ебырьметр**! Каждое сообщение пользователя может как повысить, так и понизить уровень. 
    !ебырь - вывод твоего уровня 
    !ебыри - таблица уровней""")


@commands.command(name='лвл_стоп')
async def cmd_levels_stop(ctx):
    LevelsDB().channel_unreg(ctx.channel.id)
    await ctx.message.delete()
    await ctx.channel.send(f"Канал больше не участвует в программе **Ебырьметр**")


@commands.command(name='ебырь')
async def cmd_levels_points(ctx):
    if not (points := LevelsDB().points_get(ctx.channel.id, ctx.author.id)):
        await ctx.message.reply(f"Канал не зарегистрирован в программе **Ебырьметр**")
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
    table = LevelsDB().points_table(ctx.channel.id)

    if not table:
        await ctx.message.reply(f"Канал не зарегистрирован в программе **Ебырьметр**")
        return

    table = sorted(table.items(), key=lambda v: v[1], reverse=True)

    points = [f"{i}. {name}: {convert_points(v)} см."
              for i, (p, v) in enumerate(table)
              if (name := members.get(p))]
    await ctx.message.reply('\n'.join(points))
