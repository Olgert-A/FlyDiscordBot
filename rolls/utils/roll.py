import re
from enum import Enum


class RollTypes(Enum):
    ALL = 1
    PERCENT = 2
    POINTS = 3


class RollParser:
    @staticmethod
    def parse(arg_string: str):
        patterns = [
            r'(?<!\S)(?i)all(?!\S)',
            r'(?<!\S)\d+%(?!\S)',
            r'(?<!\S)\d+(?!\S)'
        ]

        matches = (re.findall(p, arg_string) for p in patterns)
        all_in, percent, pts = matches

        if all_in:
            factor = 100.0
            roll_type = RollTypes.PERCENT
            return factor, roll_type
        elif percent:
            extracted = int(percent[0][:-1])
            factor = float(extracted / 100.0)
            roll_type = RollTypes.PERCENT
            return factor, roll_type
        elif pts:
            factor = int(pts[0])
            roll_type = RollTypes.POINTS
            return factor, roll_type
