import re


class TargetParser:
    @staticmethod
    def parce(args):
        args = ' '.join(args)
        target_strings = re.findall(r'<@\d+>\s+\d|<@\d+>|(?<!\S)\d+(?!\S)', args)
        targets = [TargetKicks(t) for t in target_strings]
        return targets


class TargetKicks:
    def __init__(self, target_string):
        self.id = self._get_id(target_string)
        self.kicks = self._get_kicks(target_string)

    def __str__(self):
        return f'{self.id}: {self.kicks}'

    @staticmethod
    def _get_id(target_string):
        result = re.findall(r'(?<=<@)\d+(?=>)', target_string)
        if result:
            return f'{result[0]}'
        else:
            return ''

    @staticmethod
    def _get_kicks(target_string):
        result = re.findall(r'(?<!\S)\d+(?!\S)', target_string)
        if result:
            return result[0]
        else:
            return 1



