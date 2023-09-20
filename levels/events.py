import random
from levels.utils import LevelUtils
from db.current import get_levels_db


class LevelEvents:
    @staticmethod
    def get_events():
        return [LevelEvents.circle,
                LevelEvents.all_to_one]

    @staticmethod
    def circle(channel_id, members):
        report = "Время круговой ебки!\n"
        random.shuffle(members)
        size = len(members)

        for current_index in range(size):
            next_index = current_index + 1
            target_index = next_index if next_index < size else next_index-size

            author_id = members[current_index].id
            target_id = members[target_index].id

            pts_up = LevelUtils.calc_kick(channel_id, author_id, target_id)

            get_levels_db().points_add(channel_id, author_id, pts_up)
            get_levels_db().points_add(channel_id, target_id, -pts_up)
            report += f"<@{author_id}> выбирает <@{target_id}> и получает {LevelUtils.convert_points(pts_up):.2f} см.\n"
        return report

    @staticmethod
    def all_to_one(channel_id, members):
        random.shuffle(members)
        victim = members[0]
        others = members[1:]
        report = f"Все на одного!\nЖертва дня - <@{victim}>\n"

        victim_points = 0
        for author in others:
            pts_up = LevelUtils.calc_kick(channel_id, author.id, victim.id)
            victim_points -= pts_up

            get_levels_db().points_add(channel_id, author.id, pts_up)
            get_levels_db().points_add(channel_id, victim.id, -pts_up)

            report += f"<@{author.id}> получает {LevelUtils.convert_points(pts_up):.2f} см.\n"

        report += f"\nСуммарно жертва получила {LevelUtils.convert_points(victim_points):.2f} см."
        return report
