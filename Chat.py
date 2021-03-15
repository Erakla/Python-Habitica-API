import HabiticaAPI.SendQueue as SendQueue
import HabiticaAPI.Exceptions as Exceptions
import time

class Chat:
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
                        self.__data['groups'][self.__group_id] = self.__send('get', 'api/v3/groups/%s' % self.__group_id, False)
                        self.__group = self.__data['groups'][self.__group_id]
                        self.__group['synctime'] = time.time()
                # if not topical... load and update
                if time.time() - self.__data['groups'][self.__group_id]['synctime'] > self.__data['cached_duration']:
                    self.__group.update(self.__send('get', 'api/v3/groups/%s' % self.__group_id, False))
                    self.__group['synctime'] = time.time()
            except Exceptions.ArgumentsNotAcceptedException as ex:
                raise Exceptions.InvalidIDException(ex, type_='user_id', id=self.__group_id)
            return func(self, *args, **kwargs)
        return inner

    # noinspection PyArgumentList
    @__refresh
    def send_message(self, message: str, queued: bool = True, callback: object = None):
        url = 'api/v3/groups/%s/chat'
        args = self.__group_id
        data = {'message': message}
        update = {
            'chatSingleMsg': self.__group_id
        }
        return self.__send('post', url % args, queued, callback, data, update)
