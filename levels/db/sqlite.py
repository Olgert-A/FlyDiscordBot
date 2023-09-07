import sqlite3
from levels.db.abstract import AbstractLevelsDB


class SqliteDb(AbstractLevelsDB):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SqliteDb, cls).__new__(cls)
        return cls.instance

    def __init__(self, database_url):
        super().__init__(database_url)
        self._connection = sqlite3.connect('levels.db')
        self._cursor = self._connection.cursor()
        self._channels_create()
        self._stats_create()

    def __del__(self):
        self._connection.close()

    def _channels_create(self):
        self._cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY, 
            channel_id INTEGER NOT NULL UNIQUE
            );""")
        self._connection.commit()

    def _stats_create(self):
        self._cursor.execute("""CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY, 
            reg_id INTEGER,
            user_id INTEGER NOT NULL,
            points INTEGER,
            FOREIGN KEY (reg_id) REFERENCES Channels (id) ON DELETE CASCADE,
            UNIQUE(reg_id, user_id)
            );""")
        self._connection.commit()

    def channel_reg(self, channel_id):
        self._cursor.execute("""INSERT INTO channels(channel_id) 
            VALUES (?) 
            ON CONFLICT(channel_id) DO NOTHING;""", (channel_id,))
        self._connection.commit()

    def channel_unreg(self, channel_id):
        self._cursor.execute("""DELETE FROM channels WHERE channel_id = ?;""", (channel_id,))
        self._connection.commit()

    def points_add(self, channel_id, user_id, points):
        self._cursor.execute("""INSERT INTO stats(reg_id, user_id, points)
            SELECT id, ?, ? FROM channels 
            WHERE channel_id = ?
            ON CONFLICT(reg_id, user_id) 
            DO UPDATE SET points = points + excluded.points;""", (user_id, points, channel_id))
        self._connection.commit()

    def channels_list(self):
        self._cursor.execute("""SELECT channel_id FROM channels""")
        self._cursor.row_factory = lambda cursor, row: row[0]
        res = self._cursor.fetchall()
        self._cursor.row_factory = None
        return res

    def points_get(self, channel_id, user_id):
        self._cursor.execute("""SELECT points FROM stats
            WHERE user_id = ?
            AND reg_id = (SELECT id FROM channels WHERE channel_id = ?)""", (user_id, channel_id))
        self._cursor.row_factory = lambda cursor, row: row[0]
        res = self._cursor.fetchone()
        self._cursor.row_factory = None
        return res

    def points_table(self, channel_id):
        self._cursor.execute("""SELECT user_id, points FROM stats
            WHERE reg_id = (SELECT id FROM channels WHERE channel_id = ?)""", (channel_id,))
        return dict(self._cursor.fetchall())


def sqlite():
    db = SqliteDb()
    db.channel_reg(123)
    db.points_add(123, 4444, 5)
    print(db.channels_list())
    print(db.points_table(123))
    print(db.points_get(123, 5555))
    print(db.points_table(123))


if __name__ == '__main__':
    sqlite()