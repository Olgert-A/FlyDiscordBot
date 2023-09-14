import os
from db.interface.levels import AbstractLevelsDB
from db.postgres.levels import LevelsDb
from db.postgres.kick import KickDb


def get_db() -> AbstractLevelsDB:
    return LevelsDb(os.getenv("DATABASE_URL"))


def get_uses_db():
    return KickDb(os.getenv("DATABASE_URL"))
