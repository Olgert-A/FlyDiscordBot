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
        report = f'Турнир! Каждый с каждым играет {matches} матчей.\n\nМатчи:\n'

        for first, second in cmb:
            scores = [winner(first.id, second.id) for _ in range(matches)]
            count = Counter(scores)
            first_pts = count[first.id]
            second_pts = count[second.id]
            table[first.id] += first_pts
            table[second.id] += second_pts
            report += f'{first_pts}:{second_pts} <@{first.id}> - <@{second.id}>\n'

        report += '\nТаблица:\n'
        sorted_table = sorted(table.items(), key=lambda item: item[1], reverse=True)
        for place, (k, v) in enumerate(sorted_table):
            report += f'{place+1}. <@{k}> {v}\n'

        top_match_pts = max(table.values())  #get top table points
        match_pts_count = Counter(table.values())  # find count of top points
        winners_count = match_pts_count[top_match_pts]
        match_reward = 500 / (winners_count * matches * (len(members) - 1))
        pts = top_match_pts * match_reward
        for w in sorted_table[:winners_count]:
            winner_id, _ = w
            get_levels_db().points_add(channel_id, winner_id, pts)
            report += (f'\nПобедитель турнира <@{winner_id}> заработал {top_match_pts} очков и получает приз в '
                       f'{LevelPoints.convert(pts):.2f} см.')
        return report


