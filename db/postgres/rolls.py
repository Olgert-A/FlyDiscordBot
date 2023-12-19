import os
import logging
import psycopg
from db.interface.rolls import AbstractRollsDB

logging.basicConfig(level=logging.INFO)


class RollsDb(AbstractRollsDB):
    def __init__(self, database_url):
        super().__init__(database_url)
        self._guilds_create()
        self._rolls_create()
        self._duels_create()

    def _drop_tables(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""DROP TABLE IF EXISTS guilds, rolls;""")

    def _guilds_create(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS guilds (
                id SERIAL PRIMARY KEY, 
                guild_id BIGINT NOT NULL UNIQUE
                );""")

    def _rolls_create(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS rolls (
                id SERIAL PRIMARY KEY, 
                reg_id SERIAL,
                user_id BIGINT NOT NULL,
                points INTEGER,
                FOREIGN KEY (reg_id) REFERENCES guilds (id) ON DELETE CASCADE,
                UNIQUE(reg_id, user_id)
                );""")

    def _duels_create(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""DROP TABLE duels;""")
            c.execute("""CREATE TABLE IF NOT EXISTS duels (
                id SERIAL PRIMARY KEY, 
                message_id BIGINT UNIQUE,
                timestamp TIMESTAMP NOT NULL,
                user_id BIGINT NOT NULL,
                target_id BIGINT NOT NULL,
                points INTEGER
                );""")

    def duels_contract_add(self, message_id, timestamp, user_id, target_id, points):
        with psycopg.connect(self.DATABASE_URL) as con:
            with con.cursor() as c:
                c.execute("""INSERT INTO duels(message_id, timestamp, user_id, target_id, points) 
                       VALUES (%s, %s, %s, %s, %s) 
                       ON CONFLICT(message_id) DO NOTHING;""", (message_id, timestamp, user_id, target_id, points))
                res = c.execute("""SELECT * FROM duels;""").fetchall()
                logging.info('add contract')
                logging.info(f'select: {res}')

    def duels_contract_get(self, message_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            #c.row_factory = lambda cursor: lambda row: row[0]
            try:
                res = c.execute("""SELECT timestamp, user_id, target_id, points
                                FROM duels WHERE message_id = %s;""", (message_id,)).fetchone()
            except psycopg.Error as e:
                logging.error(f"Get duels contract raise exception: {e}")
                return
            #finally:
                #c.row_factory = None
            print(res)
            return res

    def duel_get(self):
        with psycopg.connect(self.DATABASE_URL) as con:
            with con.cursor() as c:
                res = c.execute("""SELECT * FROM duels;""").fetchall()
                logging.info('get all duels')
                logging.info(f'select: {res}')
                return dict(res)

    def duels_contract_find(self, user_id, target_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            #c.row_factory = lambda cursor: lambda row: row[0]
            try:
                res = c.execute("""SELECT message_id, timestamp, points FROM duels 
                                WHERE user_id = %s
                                AND target_id = %s;""", (user_id, target_id)).fetchone()
            except psycopg.Error as e:
                logging.error(f"Find duels contract raise exception: {e}")
                return
            #finally:
                #c.row_factory = None
            print(res)
            return res

    def duels_contract_clear(self, message_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("DELETE FROM duels WHERE message_id = %s", (message_id,))

    def guild_reg(self, guild_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO guilds(guild_id) 
                   VALUES (%s) 
                   ON CONFLICT(guild_id) DO NOTHING;""", (guild_id,))

    def guild_reg_stop(self, guild_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("DELETE FROM guilds WHERE guild_id = %s;", (guild_id,))

    def get_guilds(self):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.row_factory = lambda cursor: lambda row: row[0]
            res = c.execute("SELECT guild_id FROM guilds").fetchall()
            c.row_factory = None
            return res

    def points_set(self, guild_id, user_id, points):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO rolls(reg_id, user_id, points)
            SELECT id, %s, %s FROM guilds 
            WHERE guild_id = %s
            ON CONFLICT(reg_id, user_id) 
            DO UPDATE SET points = excluded.points;""", (user_id, points, guild_id))

    def points_add(self, guild_id, user_id, points):
        with psycopg.connect(self.DATABASE_URL) as c:
            c.execute("""INSERT INTO rolls(reg_id, user_id, points)
            SELECT id, %s, %s FROM guilds 
            WHERE guild_id = %s
            ON CONFLICT(reg_id, user_id) 
            DO UPDATE SET points = rolls.points + excluded.points;""", (user_id, points, guild_id))

    def points_get(self, guild_id, user_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            logging.info(f"User {user_id} request points in guild {guild_id}")

            c.row_factory = lambda cursor: lambda row: row[0]
            try:
                res = c.execute(
                    """SELECT points FROM rolls
                    WHERE user_id = %s
                    AND reg_id = (SELECT id FROM guilds WHERE guild_id = %s)""",
                    (user_id, guild_id)
                                ).fetchone()
            except psycopg.Error as e:
                logging.error(f"Get points raise exception: {e}")
                return
            finally:
                c.row_factory = None
            print(res)
            return res

    def points_table(self, guild_id):
        with psycopg.connect(self.DATABASE_URL) as c:
            res = c.execute("""SELECT user_id, points FROM rolls
                WHERE reg_id = (SELECT id FROM guilds WHERE guild_id = %s)""", (guild_id,)
                            ).fetchall()

            return dict(res)
