import os
from levels.db.abstract import AbstractLevelsDB
from levels.db.postgres import PostgresDb


def get_db() -> AbstractLevelsDB:
    return PostgresDb(os.getenv("DATABASE_URL"))
