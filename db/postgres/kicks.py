import psycopg
import logging
from db.interface.kicks import AbstractKicksDb

logging.basicConfig(level=logging.INFO)


class KicksDb(AbstractKicksDb):
    def __init__(self, database_url):
        super().__init__(database_url)
        self._create()

    def _create(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS kicks (
                            id SERIAL PRIMARY KEY, 
                            reg_id SERIAL,
                            user_id BIGINT NOT NULL,
                            uses INTEGER,
                            FOREIGN KEY (reg_id) REFERENCES Channels (id) ON DELETE CASCADE,
                            UNIQUE(reg_id, user_id)
                            );""")

    def set(self, channel_id, user_id, uses):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO kicks(reg_id, user_id, uses)
            SELECT id, %s, %s FROM channels 
            WHERE channel_id = %s
            ON CONFLICT(reg_id, user_id) 
            DO UPDATE SET uses = excluded.uses;""", (user_id, uses, channel_id))

    def add(self, channel_id, user_id, uses):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO kicks(reg_id, user_id, uses)
            SELECT id, %s, %s FROM channels 
            WHERE channel_id = %s
            ON CONFLICT(reg_id, user_id) 
            DO UPDATE SET uses = kicks.uses + excluded.uses;""", (user_id, uses, channel_id))

    def get(self, channel_id, user_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.row_factory = lambda cursor: lambda row: row[0]
            try:
                res = c.execute(
                    """SELECT uses FROM kicks
                    WHERE user_id = %s
                    AND reg_id = (SELECT id FROM channels WHERE channel_id = %s)""",
                    (user_id, channel_id)
                                ).fetchone()
            except psycopg.Error as e:
                logging.error(f"Get points raise exception: {e}")
                return
            finally:
                c.row_factory = None
            return res

    def clear(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""UPDATE kicks SET uses = 0""")
