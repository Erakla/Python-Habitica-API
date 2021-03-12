from .SendQueue import SendQueue
from .Exceptions import ArgumentsNotAcceptedException, InvalidIDException
import time

class ProfileList(list):
    pass


class Profile:
    def __init__(self, data: dict, send: SendQueue, user_id: str):
        self.__data = data
        self.__send = send
        self.__user_id = user_id

    # def __reload(func):
    #     def inner(self, *args, **kwargs):
    #         if self.user_id not in self.__data['profiles'] or time.time() - self.__data['profiles'][self.user_id]['synctime'] > self.__data['cached_duration']:
    #             profile = self.__send('get', 'api/v3/members/%s' % self.user_id, False)
    #             profile['synctime'] = time.time()
    #             self.__data['profiles'][self.user_id] = profile
    #         return func(self, *args, **kwargs)
    #     return inner

    def __getitem__(self, item):
        try:
            if self.__user_id not in self.__data['profiles'] or time.time() - self.__data['profiles'][self.__user_id]['synctime'] > self.__data['cached_duration']:
                profile = self.__send('get', 'api/v3/members/%s' % self.__user_id, False)
                profile['synctime'] = time.time()
                self.__data['profiles'][self.__user_id] = profile
        except ArgumentsNotAcceptedException as ex:
            raise InvalidIDException(ex, type_='user_id', id=self.__user_id)
        return self.__data['profiles'][self.__user_id][item]
