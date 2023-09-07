import os
import psycopg
from psycopg import rows
from levels.db.abstract import AbstractLevelsDB


class PostgresDb(AbstractLevelsDB):
    def __init__(self, database_url):
        super().__init__(database_url)
        self._channels_create()
        self._stats_create()

    def _channels_create(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS channels (
                id SERIAL PRIMARY KEY, 
                channel_id BIGINT NOT NULL UNIQUE
                );""")

    def _stats_create(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS stats (
                id SERIAL PRIMARY KEY, 
                reg_id SERIAL,
                user_id BIGINT NOT NULL,
                points INTEGER,
                FOREIGN KEY (reg_id) REFERENCES Channels (id) ON DELETE CASCADE,
                UNIQUE(reg_id, user_id)
                );""")

    def channel_reg(self, channel_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO channels(channel_id) 
                   VALUES (%s) 
                   ON CONFLICT(channel_id) DO NOTHING;""", (channel_id,))

    def channel_unreg(self, channel_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("DELETE FROM channels WHERE channel_id = %s;", (channel_id,))

    def points_add(self, channel_id, user_id, points):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO stats(reg_id, user_id, points)
            SELECT id, %s, %s FROM channels 
            WHERE channel_id = %s
            ON CONFLICT(reg_id, user_id) 
            DO UPDATE SET points = stats.points + excluded.points;""", (user_id, points, channel_id))

    def points_get(self, channel_id, user_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.row_factory = lambda cursor: lambda row: row[0]
            res = c.execute(
                """SELECT points FROM stats
                WHERE user_id = %s
                AND reg_id = (SELECT id FROM channels WHERE channel_id = %s)""",
                (user_id, channel_id)
                            ).fetchone()
            c.row_factory = None
            print(res)
            return res

    def points_table(self, channel_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            res = c.execute("""SELECT user_id, points FROM stats
                WHERE reg_id = (SELECT id FROM channels WHERE channel_id = %s)""", (channel_id,)
                            ).fetchall()

            return dict(res)


def postgres():
    TOKEN = os.getenv("DATABASE_URL")
    with psycopg.connect(TOKEN) as c:
        c.execute("DROP TABLE IF EXISTS stats;")
        c.execute("DROP TABLE IF EXISTS channels;")

    #db = PostgresDb(TOKEN)
    #db.channel_reg(123)
    #db.points_add(123, 5555, 5)
    #print(db.points_table(123))


if __name__ == '__main__':
    postgres()
