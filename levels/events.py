import logging
import random
from itertools import combinations
from collections import Counter
from levels.utils.points import LevelPoints
from levels.utils.kick import LevelKick
from levels.utils.misc import LevelMisc
from db.current import get_levels_db


logging.basicConfig(level=logging.INFO)


class LevelEvents:
    @staticmethod
    def get_events():
        return [LevelEvents.circle,
                LevelEvents.all_to_one,
                LevelEvents.cut,
                LevelEvents.tournament,
                LevelEvents.team_kick]

    @staticmethod
    def circle(channel_id, members):
        logging.info('Event: circle')
        report = "Время круговой ебки!\n"
        random.shuffle(members)
        size = len(members)

        for current_index in range(size):
            next_index = current_index + 1
            target_index = next_index if next_index < size else next_index - size

            author_id = members[current_index].id
            target_id = members[target_index].id

            pts_up = LevelKick.calc_by_id(channel_id, author_id, target_id)

            get_levels_db().points_add(channel_id, author_id, pts_up)
            get_levels_db().points_add(channel_id, target_id, -pts_up)
            report += f"<@{author_id}> выбирает <@{target_id}> и получает {LevelPoints.convert(pts_up):.2f} см.\n"

        logging.info(f'Report:\n{report}')
        return report

    @staticmethod
    def all_to_one(channel_id, members):
        logging.info('Event: all_to_one')
        random.shuffle(members)
        victim = members[0]
        others = members[1:]
        report = f"Все на одного!\nЖертва дня - <@{victim.id}>\n"

        victim_points = 0
        for author in others:
            pts_up = LevelKick.calc_by_id(channel_id, author.id, victim.id)
            victim_points -= pts_up

            get_levels_db().points_add(channel_id, author.id, pts_up)
            get_levels_db().points_add(channel_id, victim.id, -pts_up)

            report += f"<@{author.id}> получает {LevelPoints.convert(pts_up):.2f} см.\n"

        report += f"\nСуммарно жертва получила {LevelPoints.convert(victim_points):.2f} см."
        logging.info(f'Report:\n{report}')
        return report

    @staticmethod
    def cut(channel_id, members):
        logging.info('Event: cut')
        victim = random.choice(members)

        pts = LevelPoints.get(channel_id, victim.id)
        cut = -random.randint(0, abs(pts))
        get_levels_db().points_add(channel_id, victim.id, cut)

        report = (f"<@{victim.id}> забрёл не в тот район, встретил бродячую собаку, которая откусила ему "
                  f"{LevelPoints.convert(-cut):.2f} см.")
        logging.info(f'Report:\n{report}')
        return report

    @staticmethod
    def tournament(channel_id, members):
        logging.info('Event: tournament')
        members_amount = len(members)
        if members_amount < 2:
            return

        members = random.sample(members, 6 if members_amount >= 6 else members_amount)

        table = {m.id: 0 for m in members}
        cmb = combinations(members, 2)
        matches = random.randint(1, 5)
        report = f'Турнир! Каждый с каждым играет {matches} матчей.\n\nУчастники:\n'
        for m in members:
            report += f'<@{m.id}>\n'

        report += '\nМатчи:\n'
        for first, second in cmb:
            scores = [LevelMisc.winner(first.id, second.id) for _ in range(matches)]
            count = Counter(scores)
            first_pts = count[first.id]
            second_pts = count[second.id]
            table[first.id] += first_pts
            table[second.id] += second_pts
            report += f'{first_pts}:{second_pts} <@{first.id}> - <@{second.id}>\n'

        report += '\nТаблица:\n'
        sorted_table = sorted(table.items(), key=lambda item: item[1], reverse=True)
        for place, (k, v) in enumerate(sorted_table):
            report += f'{place + 1}. <@{k}> {v}\n'

        top_match_pts = max(table.values())  # get top table points
        match_pts_count = Counter(table.values())  # find count of points
        winners_count = match_pts_count[top_match_pts]  # get count of top points
        match_reward = 500 / (winners_count * matches * (len(members) - 1))  # calc reward
        pts = top_match_pts * match_reward  # calc points
        for winner in sorted_table[:winners_count]:
            winner_id, _ = winner
            get_levels_db().points_add(channel_id, winner_id, pts)
            report += (f'\nПобедитель турнира <@{winner_id}> заработал {top_match_pts} очков и получает приз в '
                       f'{LevelPoints.convert(pts):.2f} см.')

        logging.info(f'Report:\n{report}')
        return report

    @staticmethod
    def team_kick(channel_id, members):
        logging.info('Event: team_kick')
        members_amount = len(members)
        if members_amount < 4:
            return

        team_size = random.randint(2, int(members_amount / 2))
        selected = random.sample(members, team_size * 2)

        team1 = selected[:team_size]
        team2 = selected[-team_size:]

        report = 'Командная ебка!\n\nКоманда №1:\n'
        for m in team1:
            report += f'<@{m.id}>\n'
        report += '\nКоманда №2:\n'
        for m in team2:
            report += f'<@{m.id}>\n'

        team1_pts = {m.id: get_levels_db().points_get(channel_id, m.id) for m in team1}
        team2_pts = {m.id: get_levels_db().points_get(channel_id, m.id) for m in team2}
        team1_sum = sum(team1_pts.values())
        team2_sum = sum(team2_pts.values())
        kick_result = LevelKick.calc_by_pts(team1_sum, team2_sum)
        logging.info(f'team1: {team1_pts}\nsum: {team1_sum}\nteam2: {team2_pts}\nsum: {team2_sum}\nkick: {kick_result}')

        report += (f'\nКоманда 1 вступает в гачи-поединок с Командой 2 и получает '
                   f'{LevelPoints.convert(kick_result):.2f} см.\n\nРаспределение очков:\n')

        for m_id, m_pts in team1_pts.items():
            pts = int(kick_result * m_pts / team1_sum)
            get_levels_db().points_add(channel_id, m_id, pts)
            report += f'<@{m_id}> получает {LevelPoints.convert(pts):.2f} см.\n'

        for m_id, m_pts in team2_pts.items():
            pts = -int(kick_result * m_pts / team2_sum)
            get_levels_db().points_add(channel_id, m_id, pts)
            report += f'<@{m_id}> получает {LevelPoints.convert(pts):.2f} см.\n'

        logging.info(f'Report:\n{report}')
        return report
