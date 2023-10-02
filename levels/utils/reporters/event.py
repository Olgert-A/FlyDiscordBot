from collections import Counter
from levels.utils.reporters.base import BaseReporter
from levels.utils.points import LevelPoints
from levels.utils.misc import LevelMisc

name = LevelMisc.name
convert = LevelPoints.convert


class CircleReporter(BaseReporter):
    def __init__(self):
        super().__init__()
        self.event_name = 'Круговая ебка!'
        self.awaited_data_keys = ['actions']

    def create_report(self) -> str:
        report = f"{self.event_name}\n"
        for author, target, pts in self.data['actions']:
            report += f"<@{author.id}> выбирает {name(target)} и получает {convert(pts):.2f} см.\n"
        return report


class AllToOneReporter(BaseReporter):
    def __init__(self):
        super().__init__()
        self.event_name = 'Все на одного!'
        self.awaited_data_keys = ['victim', 'actions', 'victim_pts']

    def create_report(self) -> str:
        victim, victim_pts = self.data['victim'], self.data['victim_pts']

        report = f"{self.event_name}\n"
        report += f'Жертва дня - <@{victim.id}>\n'
        for author, pts in self.data['actions']:
            report += f"<@{author.id}> получает {convert(pts):.2f} см.\n"
        report += f"\nСуммарно жертва получила {convert(victim_pts):.2f} см."
        return report


class TournamentReporter(BaseReporter):
    def __init__(self):
        super().__init__()
        self.event_name = 'Турнир!'
        self.awaited_data_keys = ['competitors', 'matches_count', 'matches', 'table', 'winners', 'reward']

    def create_report(self) -> str:
        matches_count, table, reward = self.data['matches_count'], self.data['table'], self.data['reward']
        # LevelMisc.name need discord.Member, but table keys are discord.Member.id. Create temp converter dict:
        member_by_id = {c.id: c for c in self.data['competitors']}

        # show event name
        report = f"{self.event_name} Каждый с каждым играет {matches_count} матчей!\n\n"

        # show competitors
        report += 'Участники:\n'
        for competitor in self.data['competitors']:
            report += f'<@{competitor.id}>\n'

        # show all matches with score
        report += '\nМатчи:\n'
        for first, second, matches in self.data['matches']:
            count = Counter(matches)
            first_pts, second_pts = count[first.id], count[second.id]
            report += f'{first_pts}:{second_pts} {name(first)} - {name(second)}\n'

        # show score table sorted by score
        report += '\nТаблица:\n'
        sorted_table = sorted(table.items(), key=lambda item: item[1], reverse=True)
        for place, (k, v) in enumerate(sorted_table):
            report += f'{place + 1}. {name(member_by_id[k])} {v}\n'

        # show winners text
        for winner_id in self.data['winners']:
            report += (f'\nПобедитель турнира {name(member_by_id[winner_id])} получает '
                       f'приз в {convert(reward):.2f} см.')

        return report
