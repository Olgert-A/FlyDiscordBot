import psycopg
import logging

logging.basicConfig(level=logging.INFO)


class KickDb:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KickDb, cls).__new__(cls)
        return cls.instance

    def __init__(self, database_url):
        self.DATABASE_URL = database_url
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

    def update(self, channel_id, user_id, uses):
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
            print(res)
            return res

    def clear(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""UPDATE kicks SET uses = 0""")
