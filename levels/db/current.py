import os
from levels.db.abstract import AbstractLevelsDB
from levels.db.postgres import PostgresDb
from levels.db.kick import KickDb


def get_db() -> AbstractLevelsDB:
    return PostgresDb(os.getenv("DATABASE_URL"))


def get_uses_db():
    return KickDb(os.getenv("DATABASE_URL"))