import random
from itertools import combinations
from collections import Counter
from levels.utils.points import LevelPoints
from levels.utils.kick import LevelKick
from db.current import get_levels_db


class LevelEvents:
    @staticmethod
    def get_events():
        return [LevelEvents.circle,
                LevelEvents.all_to_one,
                LevelEvents.cut]

    @staticmethod
    def circle(channel_id, members):
        report = "Время круговой ебки!\n"
        random.shuffle(members)
        size = len(members)

        for current_index in range(size):
            next_index = current_index + 1
            target_index = next_index if next_index < size else next_index-size

            author_id = members[current_index].id
            target_id = members[target_index].id

            pts_up = LevelKick.calc(channel_id, author_id, target_id)

            get_levels_db().points_add(channel_id, author_id, pts_up)
            get_levels_db().points_add(channel_id, target_id, -pts_up)
            report += f"<@{author_id}> выбирает <@{target_id}> и получает {LevelPoints.convert(pts_up):.2f} см.\n"
        return report

    @staticmethod
    def all_to_one(channel_id, members):
        random.shuffle(members)
        victim = members[0]
        others = members[1:]
        report = f"Все на одного!\nЖертва дня - <@{victim.id}>\n"

        victim_points = 0
        for author in others:
            pts_up = LevelKick.calc(channel_id, author.id, victim.id)
            victim_points -= pts_up

            get_levels_db().points_add(channel_id, author.id, pts_up)
            get_levels_db().points_add(channel_id, victim.id, -pts_up)

            report += f"<@{author.id}> получает {LevelPoints.convert(pts_up):.2f} см.\n"

        report += f"\nСуммарно жертва получила {LevelPoints.convert(victim_points):.2f} см."
        return report

    @staticmethod
    def cut(channel_id, members):
        victim = random.choice(members)

        pts = LevelPoints.get(channel_id, victim.id)
        cut = -random.randint(0, abs(pts))
        get_levels_db().points_add(channel_id, victim.id, cut)

        return (f"<@{victim.id}> забрёл не в тот район, встретил бродячую собаку, которая откусила ему "
                  f"{LevelPoints.convert(-cut):.2f} см.")

    @staticmethod
    def tournament(channel_id, members):
        def winner(first, second):
            return random.choice([first, second])

        if len(members) < 2:
            return

        table = {m.id: 0 for m in members}

        cmb = combinations(members, 2)
        matches = random.randint(1, 5)
        report = f'Турнир! Каждый с каждым играет {matches} матчей.\n\nМатчи:'

        for first, second in cmb:
            scores = [winner(first.id, second.id) for _ in range(matches)]
            count = Counter(scores)
            first_pts = count[first.id]
            second_pts = count[second.id]
            table[first.id] += first_pts
            table[second.id] += second_pts
            report += f'{first_pts}:{second_pts} <@{first.id}> : <@{second.id}>\n'

        report += '\n Таблица:'
        sorted_table = sorted(table, key=lambda k: table[k], reverse=True)
        for place, (k, v) in enumerate(sorted_table):
            report += f'{place}. <@{k}> {v}\n'

        top_score, _ = sorted_table[0]#max(table, key=lambda k: table[k])
        match_reward = 500 / (matches * (len(members) - 1))
        pts = table[top_score] * match_reward
        report += (f'\nПобедитель турнира <@{top_score}> заработал {table[top_score]} очков и получает приз в '
                   f'{LevelPoints.convert(pts):.2f} см.')
        return report


