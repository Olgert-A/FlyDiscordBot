import re
from typing import List


class MemberIdKicks:
    """
    Represent target parsed from command parameters string
    :param id: - discord.Member.id parsed or TARGET_RANDOM
    :param kicks: - kicks parsed or DEFAULT_KICKS
    """
    TARGET_RANDOM = -1
    DEFAULT_KICKS = 1

    def __init__(self, target_string):
        self.id: int = MemberIdKicks._extract_data(target_string,
                                                   r'(?<=<@)\d+(?=>)',
                                                   MemberIdKicks.TARGET_RANDOM)
        self.kicks: int = MemberIdKicks._extract_data(target_string,
                                                      r'(?<!\S)\d+(?!\S)',
                                                      MemberIdKicks.DEFAULT_KICKS)

    def __str__(self):
        return f'Parsed member with id={self.id} and kicks={self.kicks}'

    @staticmethod
    def _extract_data(string: str, extract_condition: str, default_value: int) -> int:
        result = re.findall(extract_condition, string)
        return int(result[0]) if result else default_value


class TargetParser:
    @staticmethod
    def parce(arg_string: str) -> List[MemberIdKicks]:
        """
        Parce arg_string to list of MemberIdKicks data classes.

        N kicks without target will be interpreted as one kick of N random targets.

        If arg_string can't be parsed, return one target with MemberIdKicks TARGET_RANDOM and DEFAULT_KICKS constants
        """
        target_strings = re.findall(r'<@\d+>\s+\d+|<@\d+>|(?<!\S)\d+(?!\S)', arg_string)
        targets = [MemberIdKicks(t) for t in target_strings]
        if not targets:
            targets.append(MemberIdKicks('1'))

        # N-random kicks mean 1 kick of N random targets (not N kicks of one random target).
        # need to divide into several random targets with kicks=1 if MemberIdKicks with id=TARGET_RANDOM have kicks > 1
        result = []
        for target in targets:
            if target.id == MemberIdKicks.TARGET_RANDOM:
                for _ in range(target.kicks):
                    result.append(MemberIdKicks('1'))
            else:
                result.append(target)

        return result
