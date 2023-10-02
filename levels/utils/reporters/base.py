import logging
from abc import ABC, abstractmethod


class BaseReporter(ABC):
    def __init__(self):
        self.data = {}
        self.awaited_data_keys = []
        self.CHECK_ERROR_STR = 'Ивент прошёл успешно, но хуесос программист не смог зарепортить отчёт'

    @abstractmethod
    def create_report(self) -> str:
        pass

    def collect(self,
                data_key: str,
                *args: object,
                as_list: bool = False):
        """Collect data to dict using data_key.

        Single parameter will be collected as is.
        Many args will be packed to tuple.

        as_list = False - by default, collected data is assumed to be a single value. Every call of collect will replace
        collected data with new values.

        as_list = True - if args are a repeated part of a large amount of data, set  and data by data_ket will be list
        object. Every call of collect will add args as new element of list.
        """
        if not data_key or not args:
            return

        data = args[0] if len(args) == 1 else tuple(args)
        if as_list:
            if self.data.get(data_key) is None:
                self.data[data_key] = []

            self.data[data_key].append(data)
        else:
            self.data[data_key] = data

    def get_report(self) -> str:
        if not self._check_collected():
            return self.CHECK_ERROR_STR

        report = self.create_report()
        logging.info(f'Report:\n{report}')
        return report

    def _check_collected(self):
        checks = [self.data.get(key) is not None
                  for key in self.awaited_data_keys]
        return all(checks)


