import HabiticaAPI.SendQueue as SendQueue
import HabiticaAPI.Exceptions as Exceptions
import time

class Chat:
    def __init__(self, data: dict, group_id: str):
        self.__data = data
        self.__group_id = group_id
        self.__group = None
        if group_id in data['groups']:
            self.__group = self.__data['groups'][self.__group_id]
        else:
            self.__group = None

    def refresh(self):
        # if not assigned, load and assign
        if not self.__group:
            self.__data['groups'][self.__group_id] = self.__data['send']('get', 'api/v3/groups/%s' % self.__group_id, False)
            self.__group = self.__data['groups'][self.__group_id]
            self.__group['synctime'] = time.time()
            self.__group['members_synctime'] = 0
        # if not topical... load and update
        elif time.time() - self.__group['synctime'] > self.__data['cached_duration']:
            self.__group.update(self.__data['send']('get', 'api/v3/groups/%s' % self.__group_id, False))
            self.__group['synctime'] = time.time()

    def __refresh(func):
        def inner(self, *args, **kwargs):
            try:
                self.refresh
            except Exceptions.ArgumentsNotAcceptedException as ex:
                raise Exceptions.InvalidIDException(ex, type_='group_id', id=self.__group_id)
            return func(self, *args, **kwargs)
        return inner

    def __getitem__(self, item):
        return self.content[item]

    def __iter__(self):
        return iter(self.content)

    # noinspection PyArgumentList
    @property
    @__refresh
    def content(self):
        return self.__group['chat']

    # noinspection PyArgumentList
    @__refresh
    def send_message(self, message: str, queued: bool = True, callback: object = None):
        url = 'api/v3/groups/%s/chat'
        args = self.__group_id
        data = {'message': message}
        update = {
            'chatSingleMsg': self.__group_id
        }
        return self.__data['send']('post', url % args, queued, callback, data, update)