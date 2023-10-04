import random
import logging
from db.current import get_levels_db, get_kicks_db
from levels.utils.points import LevelPoints

logging.basicConfig(level=logging.INFO)
convert = LevelPoints.convert


class LevelKick:
    MAX_KICK_USES = 3

    @staticmethod
    def get_uses(channel_id, author_id):
        return get_kicks_db().get(channel_id, author_id)

    @staticmethod
    def add_use(channel_id, author_id):
        get_kicks_db().add(channel_id, author_id, 1)

    @staticmethod
    def calc_by_pts(author_pts, target_pts):
        def calc_chance(pts_delta):
            # calc win chance for author if author pts < target pts
            # chance y = f(x)
            # need to min x=0.5
            # get x=0.5 y=0.5 | x=2.5 y~0.7 | x=5 y~0.8 | x=10+ y=0.9
            return 1 - 1 / (pow(convert(pts_delta) + 0.5, 0.8) + 1)

        def calc_sign(pts_delta):
            value = random.randint(1, 100)
            chance = 100 * calc_chance(pts_delta)
            win = value < chance if author_pts < target_pts else value > chance
            return 1 if win else -1

        def get_min_pts(to_value):
            for x in range(100000):
                if abs(convert(x) - to_value) < 0.001:
                    return x

        delta = abs(author_pts - target_pts)
        min_pts = get_min_pts(0.5)
        delta = delta if delta > min_pts else min_pts

        sign = calc_sign(delta)
        reward = random.randint(min_pts, delta)
        logging.info(f'sign:{sign} reward:{reward}')
        return int(reward * sign)

    @staticmethod
    def calc_by_id(channel_id, author_id, target_id) -> int:
        author_pts = LevelPoints.get(channel_id, author_id)
        target_pts = LevelPoints.get(channel_id, target_id)
        logging.info(f'author_pts {author_pts}, target_pts {target_pts}')
        return LevelKick.calc_by_pts(author_pts, target_pts)

    @staticmethod
    def execute(channel_id, author_id, target_id):
        pts_up = LevelKick.calc_by_id(channel_id, author_id, target_id)
        get_levels_db().points_add(channel_id, author_id, pts_up)
        get_levels_db().points_add(channel_id, target_id, -pts_up)
        return pts_up
