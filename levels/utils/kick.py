import random
import logging
from db.current import get_levels_db, get_kicks_db
from levels.utils.points import LevelPoints

logging.basicConfig(level=logging.INFO)


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
        pts = random.randint(0, abs(author_pts - target_pts))
        chance = random.randint(-author_pts, target_pts) / max([abs(author_pts), abs(target_pts), 1])
        return int(pts * chance)

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
