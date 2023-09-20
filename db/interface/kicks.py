from abc import ABC, abstractmethod
from db.singleton import SingletonDB


class AbstractKicksDb(SingletonDB):
    def __init__(self, database_url):
        super().__init__(database_url)

    @abstractmethod
    def _create(self): pass

    @abstractmethod
    def set(self, channel_id, user_id, uses): pass

    @abstractmethod
    def add(self, channel_id, user_id, uses): pass

    @abstractmethod
    def get(self, channel_id, user_id): pass

    @abstractmethod
    def clear(self): pass
