from .SendQueue import SendQueue
from .Exceptions import ArgumentsNotAcceptedException, InvalidIDException
import time

class GroupList(list):
    pass

class Group:
    def __init__(self, data: dict, send: SendQueue, group_id: str):
        self.__data = data
        self.__send = send
        self.__group_id = group_id

    def __getitem__(self, item):
        try:
            if self.__group_id not in self.__data['groups'] or time.time() - self.__data['groups'][self.__group_id]['synctime'] > self.__data['cached_duration']:
                group = self.__send('get', 'api/v3/groups/%s' % self.__group_id, False)
                group['synctime'] = time.time()
                self.__data['profiles'][self.__group_id] = group
        except ArgumentsNotAcceptedException as ex:
            raise InvalidIDException(ex, type_='group_id', id=self.__group_id)
        return self.__data['profiles'][self.__group_id][item]
