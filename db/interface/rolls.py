from abc import ABC, abstractmethod
from db.singleton import SingletonDB


class AbstractRollsDB(ABC, SingletonDB):
    def __init__(self, database_url):
        super().__init__(database_url)

    @abstractmethod
    def _guilds_create(self): pass

    @abstractmethod
    def _rolls_create(self): pass

    @abstractmethod
    def guild_reg(self, channel_id): pass

    @abstractmethod
    def guild_reg_stop(self, channel_id): pass

    @abstractmethod
    def get_guilds(self): pass

    @abstractmethod
    def points_set(self, guild_id, user_id, points): pass

    @abstractmethod
    def points_add(self, guild_id, user_id, points): pass

    @abstractmethod
    def points_get(self, guild_id, user_id): pass

    @abstractmethod
    def points_table(self, guild_id): pass

    @abstractmethod
    def duels_add(self, message_id, user_id, target_id, points, timestamp): pass

    @abstractmethod
    def duels_get_by_id(self, message_id): pass

    @abstractmethod
    def is_contract_exist(self, user_id_to_find, target_id_to_find): pass

    @abstractmethod
    def duel_clear(self, message_id): pass

    @abstractmethod
    def _duels_create(self): pass

    @abstractmethod
    def duels_contract_add(self, message_id, timestamp): pass

    @abstractmethod
    def duels_contract_get(self, message_id): pass

    @abstractmethod
    def duel_get(self): pass

    @abstractmethod
    def duels_contract_find(self, user_id, target_id): pass

    @abstractmethod
    def duels_contract_clear(self, message_id): pass

