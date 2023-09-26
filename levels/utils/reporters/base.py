from abc import ABC, abstractmethod


class BaseReporter(ABC):
    def __init__(self, event_name=''):
        self.collected_data = {'event_name': event_name}
        self.awaited_data_keys = []
        self.CHECK_ERROR_STR = 'Ивент прошёл успешно, но хуесос программист не смог зарепортить отчёт'

    def _check_collected(self):
        checks = [self.collected_data.get(key) is not None
                  for key in self.awaited_data_keys]
        return all(checks)

    def collect(self, data_key, **kwargs):
        if not data_key or not kwargs:
            return

        if self.collected_data.get(data_key) is None:
            self.collected_data[data_key] = []

        self.collected_data[data_key].append(kwargs)

    @abstractmethod
    def get_report(self) -> str:
        pass
