import random
from db.current import get_levels_db, get_kicks_db
from levels.utils.points import LevelPoints


class LevelKick:
    MAX_KICK_USES = 3

    @staticmethod
    def get_uses(channel_id, author_id):
        return get_kicks_db().get(channel_id, author_id)

    @staticmethod
    def calc(channel_id, author_id, target_id) -> int:
        author_pts = LevelPoints.get(channel_id, author_id)
        target_pts = LevelPoints.get(channel_id, target_id)
        pts = random.randint(0, abs(author_pts - target_pts))
        chance = random.randint(-author_pts, target_pts) / max([author_pts, target_pts])
        return int(pts * chance)

    @staticmethod
    def execute(channel_id, author_id, target_id):
        pts_up = LevelKick.calc(channel_id, author_id, target_id)
        get_levels_db().points_add(channel_id, author_id, pts_up)
        get_levels_db().points_add(channel_id, target_id, -pts_up)
        get_kicks_db().add(channel_id, author_id, 1)
        return f"Ты подкрадываешься к <@{target_id}> и делаешь {random.randint(1, 10)} фрикций, " \
               f"получив {LevelPoints.convert(pts_up):.2f} см."