import random
from db.current import get_levels_db, get_kicks_db


class LevelUtils:
    MAX_KICK_USES = 3

    @staticmethod
    def generate_points():
        return random.randint(-6, 10)

    @staticmethod
    def convert_points(points):
        return points / 100.

    @staticmethod
    def get_points(channel_id, member_id):
        return get_levels_db().points_get(channel_id, member_id)

    @staticmethod
    def get_members(channel):
        return [m for m in channel.members if not m.bot]

    @staticmethod
    def get_target_id(target, members):
        # if m.id in target return m.id else return None
        for m in members:
            if str(m.id) in target:
                return m.id

    @staticmethod
    def get_kicks_use(channel_id, author_id):
        return get_kicks_db().get(channel_id, author_id)

    @staticmethod
    def calc_kick(channel_id, author_id, target_id) -> int:
        author_pts = LevelUtils.get_points(channel_id, author_id)
        target_pts = LevelUtils.get_points(channel_id, target_id)
        pts = random.randint(0, abs(author_pts - target_pts))
        chance = random.randint(-author_pts, target_pts) / max([author_pts, target_pts])
        return int(pts * chance)

    @staticmethod
    def kick(channel_id, author_id, target_id):
        pts_up = LevelUtils.calc_kick(channel_id, author_id, target_id)
        get_levels_db().points_add(channel_id, author_id, pts_up)
        get_levels_db().points_add(channel_id, target_id, -pts_up)
        get_kicks_db().add(channel_id, author_id, 1)
        return f"Ты подкрадываешься к <@{target_id}> и делаешь {random.randint(1, 10)} фрикций, " \
               f"получив {LevelUtils.convert_points(pts_up):.2f} см."

    @staticmethod
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
