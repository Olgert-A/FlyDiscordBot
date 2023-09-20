from abc import ABC, abstractmethod
from db.singleton import SingletonDB


class AbstractLevelsDB(ABC, SingletonDB):
    def __init__(self, database_url):
        super().__init__(database_url)

    @abstractmethod
    def _channels_create(self): pass

    @abstractmethod
    def _stats_create(self): pass

    @abstractmethod
    def channel_reg(self, channel_id): pass

    @abstractmethod
    def channel_reg_stop(self, channel_id): pass

    @abstractmethod
    def points_set(self, channel_id, user_id, points): pass

    @abstractmethod
    def points_add(self, channel_id, user_id, points): pass

    @abstractmethod
    def points_get(self, channel_id, user_id): pass

    @abstractmethod
    def points_table(self, channel_id): pass
