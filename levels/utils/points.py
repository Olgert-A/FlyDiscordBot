import random
from db.current import get_levels_db


class LevelPoints:
    @staticmethod
    def generate():
        return random.randint(-6, 10)

    @staticmethod
    def convert(points):
        return points / 100.

    @staticmethod
    def get(channel_id, member_id):
        return get_levels_db().points_get(channel_id, member_id)