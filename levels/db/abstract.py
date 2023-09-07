from abc import ABC, abstractmethod


class AbstractLevelsDB(ABC):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AbstractLevelsDB, cls).__new__(cls)
        return cls.instance

    def __init__(self, database_url):
        self.DATABASE_URL = database_url

    @abstractmethod
    def _channels_create(self): pass

    @abstractmethod
    def _stats_create(self): pass

    @abstractmethod
    def channel_reg(self, channel_id): pass

    @abstractmethod
    def channel_unreg(self, channel_id): pass

    @abstractmethod
    def points_add(self, channel_id, user_id, points): pass

    @abstractmethod
    def points_get(self, channel_id, user_id): pass

    @abstractmethod
    def points_table(self, channel_id): pass








