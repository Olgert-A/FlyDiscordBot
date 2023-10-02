import os
from db.interface.levels import AbstractLevelsDB
from db.postgres.levels import LevelsDb
from db.postgres.kicks import KicksDb
from db.postgres.events import EventsDb


def get_levels_db() -> AbstractLevelsDB:
    return LevelsDb(os.getenv("DATABASE_URL"))


def get_kicks_db():
    return KicksDb(os.getenv("DATABASE_URL"))


def get_events_db():
    return EventsDb(os.getenv("DATABASE_URL"))
