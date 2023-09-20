import os
from db.interface.levels import AbstractLevelsDB
from db.postgres.levels import LevelsDb
from db.postgres.kicks import KicksDb


def get_levels_db() -> AbstractLevelsDB:
    return LevelsDb(os.getenv("DATABASE_URL"))


def get_kicks_db():
    return KicksDb(os.getenv("DATABASE_URL"))
