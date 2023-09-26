from levels.utils.reporters.base import BaseReporter
from levels.utils.points import LevelPoints
from levels.utils.misc import LevelMisc

name = LevelMisc.name
convert = LevelPoints.convert


class CircleReporter(BaseReporter):
    def __init__(self):
        super().__init__('Круговая ебка!')
        self.awaited_data_keys = ['actions']

    def get_report(self) -> str:
        if not self._check_collected():
            return self.CHECK_ERROR_STR

        data = self.collected_data
        event_name = data['event_name']

        report = f'{event_name}\n'
        for action in data['actions']:
            author, target, pts = action['author'], action['target'], action['pts']
            report += f"<@{author.id}> выбирает {name(target)} и получает {convert(pts):.2f} см.\n"
        return report
