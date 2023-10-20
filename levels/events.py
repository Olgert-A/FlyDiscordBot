import logging
import random
import discord
from itertools import combinations
from typing import List
from levels.utils.points import LevelPoints
from levels.utils.kick import LevelKick
from levels.utils.misc import LevelMisc
from levels.utils.reporters import *
from db.current import get_levels_db

logging.basicConfig(level=logging.INFO)
name = LevelMisc.name
convert = LevelPoints.convert
levels_db = get_levels_db()


class LevelEvents:
    @staticmethod
    def get_events():
        return [LevelEvents.circle,
                LevelEvents.all_to_one,
                LevelEvents.cut,
                LevelEvents.tournament,
                LevelEvents.team_kick,
                LevelEvents.extension]

    @staticmethod
    def circle(channel_id, members):
        logging.info('Event: circle')
        reporter = CircleReporter()
        random.shuffle(members)
        size = len(members)

        for current_index in range(size):
            next_index = current_index + 1
            target_index = next_index if next_index < size else next_index - size

            author, target = members[current_index], members[target_index]
            pts_up = LevelKick.calc_by_id(channel_id, author.id, target.id)
            levels_db.points_add(channel_id, author.id, pts_up)
            levels_db.points_add(channel_id, target.id, -pts_up)
            reporter.collect('actions', author, target, pts_up, as_list=True)

        return reporter.get_report()

    @staticmethod
    def all_to_one(channel_id, members):
        logging.info('Event: all_to_one')
        random.shuffle(members)
        victim, others = members[0], members[1:]
        reporter = AllToOneReporter()
        reporter.collect('victim', victim)

        victim_points = 0
        for author in others:
            pts_up = LevelKick.calc_by_id(channel_id, author.id, victim.id)
            victim_points -= pts_up

            levels_db.points_add(channel_id, author.id, pts_up)
            levels_db.points_add(channel_id, victim.id, -pts_up)
            reporter.collect('actions', author, pts_up, as_list=True)

        reporter.collect('victim_pts', victim_points)
        return reporter.get_report()

    @staticmethod
    def cut(channel_id, members):
        logging.info('Event: cut')
        victim = random.choice(members)

        pts = LevelPoints.get(channel_id, victim.id)
        cut = -random.randint(0, abs(pts))
        levels_db.points_add(channel_id, victim.id, cut)

        report = (f"<@{victim.id}> забрёл не в тот район, встретил бродячую собаку, которая откусила ему "
                  f"{convert(-cut):.2f} см.")
        logging.info(f'Report:\n{report}')
        return report

    @staticmethod
    def tournament(channel_id, members):
        logging.info('Event: tournament')
        reporter = TournamentReporter()
        members_amount = len(members)
        if members_amount < 2:
            return

        matches_count = random.randint(1, 5)
        members = random.sample(members, 6 if members_amount >= 6 else members_amount)
        table = {m.id: 0 for m in members}

        for first, second in combinations(members, 2):
            matches = [LevelMisc.winner(first.id, second.id) for _ in range(matches_count)]

            for winner_id in matches:
                table[winner_id] += 1
            reporter.collect('matches', first, second, matches, as_list=True)

        win_score = max(table.values())
        winners = [m_id for m_id, score in table.items() if score == win_score]  # get winners
        #pts_for_match = 500 / (len(winners) * matches_count * (members_amount - 1))  # calc reward for 1 match
        all_player_match_count = (len(members) - 1) * matches_count
        reward = 500 * win_score / all_player_match_count

        for winner_id in winners:
            levels_db.points_add(channel_id, winner_id, reward)

        reporter.collect('competitors', members)
        reporter.collect('matches_count', matches_count)
        reporter.collect('table', table)
        reporter.collect('winners', winners)
        reporter.collect('reward', reward)

        return reporter.get_report()

    @staticmethod
    def team_kick(channel_id, members):
        logging.info('Event: team_kick')
        members_amount = len(members)
        if members_amount < 4:
            return

        team_size = random.randint(2, int(members_amount / 2))
        selected = random.sample(members, team_size * 2)
        member_by_id = {m.id: m for m in selected}

        team1 = selected[:team_size]
        team2 = selected[-team_size:]

        report = 'Командная ебка!\n\nКоманда №1:\n'
        for m in team1:
            report += f'<@{m.id}>\n'
        report += '\nКоманда №2:\n'
        for m in team2:
            report += f'<@{m.id}>\n'

        team1_pts = {m.id: levels_db.points_get(channel_id, m.id) for m in team1}
        team2_pts = {m.id: levels_db.points_get(channel_id, m.id) for m in team2}
        team1_sum = sum(team1_pts.values())
        team2_sum = sum(team2_pts.values())
        kick_result = LevelKick.calc_by_pts(team1_sum, team2_sum)
        logging.info(f'team1: {team1_pts}\nsum: {team1_sum}\nteam2: {team2_pts}\nsum: {team2_sum}\nkick: {kick_result}')

        report += (f'\nКоманда 1 вступает в гачи-поединок с Командой 2 и получает '
                   f'{convert(kick_result):.2f} см.\n\nРаспределение очков:\n')

        for m_id, m_pts in team1_pts.items():
            pts = int(kick_result * m_pts / max([team1_sum, 1]))
            levels_db.points_add(channel_id, m_id, pts)
            report += f'{name(member_by_id[m_id])} получает {convert(pts):.2f} см.\n'

        for m_id, m_pts in team2_pts.items():
            pts = -int(kick_result * m_pts / max([team2_sum, 1]))
            levels_db.points_add(channel_id, m_id, pts)
            report += f'{name(member_by_id[m_id])} получает {convert(pts):.2f} см.\n'

        logging.info(f'Report:\n{report}')
        return report

    @staticmethod
    def extension(channel_id, members: List[discord.Member]):
        logging.info('Event: extension')
        report = 'В чат входит огромный волосатый негр и пристально высматривает цель!\n'
        event_pts = 500
        members_amount = len(members)
        target_amount = 1
        targets = random.sample(members, target_amount if target_amount <= members_amount else members_amount)

        for num, target in enumerate(targets):
            targets_left = target_amount - num - 1
            max_pts = event_pts - 100 * targets_left
            pts = random.randint(100, max_pts)
            levels_db.points_add(channel_id, target.id, pts)
            report += f'Выбор пал на <@{target.id}>, который получает {convert(pts):.2f} см.\n'
            event_pts -= pts

        logging.info(f'Report:\n{report}')
        return report
