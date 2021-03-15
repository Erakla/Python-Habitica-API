import HabiticaAPI.SendQueue as SendQueue
import HabiticaAPI.Exceptions as Exceptions
import HabiticaAPI.Profile as Profile
import time

class GroupList:
    pass

class Group:
    def __init__(self, data: dict, send: SendQueue.SendQueue, group_id: str):
        self.__data = data
        self.__send = send
        self.__group_id = group_id
        self.__group = None

    def __refresh(func):
        def inner(self, *args, **kwargs):
            try:
                # if not assigned
                if not self.__group:
                    # but existant... assign
                    if self.__group_id in self.__data['groups']:
                        self.__group = self.__data['groups'][self.__group_id]
                    else:  # or load and assign
                        self.__data['groups'][self.__group_id] = self.__send('get', 'https://habitica.com/api/v3/groups/%s' % self.__group_id, False)
                        self.__group = self.__data['groups'][self.__group_id]
                        self.__group['synctime'] = time.time()
                # if assigned but not topical... load and update
                elif time.time() - self.__data['groups'][self.__group_id]['synctime'] > self.__data['cached_duration']:
                    self.__group.update(self.__send('get', 'https://habitica.com/api/v3/groups/%s' % self.__group_id, False))
                    self.__group['synctime'] = time.time()
            except Exceptions.ArgumentsNotAcceptedException as ex:
                raise Exceptions.InvalidIDException(ex, type_='user_id', id=self.__group_id)
            return func(self, *args, **kwargs)
        return inner

    # noinspection PyArgumentList
    @__refresh
    def __getitem__(self, item):
        return self.content[item]

    # noinspection PyArgumentList
    @property
    @__refresh
    def content(self):
        return self.__group

    # noinspection PyArgumentList
    @property
    @__refresh
    def member(self):
        return Profile.ProfileList(self.__data, self.__send, *list(self.__group['quest']['members'].keys()))
