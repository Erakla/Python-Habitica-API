import time
from typing import Any

from .SendQueue import SendQueue

class ProfileList(list):
    pass

class Profile:
    def __init__(self, data: dict, send: SendQueue, user_id: str):
        self.__data = data
        self.__send = send
        self.user_id = user_id

    def __reload(func):
        def inner(self, *args, **kwargs):
            if self.user_id not in self.__data['profiles'] or time.time() - self.__data['profiles'][self.user_id]['synctime'] > self.__data['cached_duration']:
                profile = self.__send('get', 'api/v3/members/%s' % self.user_id, False)
                profile['synctime'] = time.time()
                self.__data['profiles'][self.user_id] = profile
            return func(self, *args, **kwargs)
        return inner

    # noinspection PyArgumentList
    @__reload
    def say_hello(self):
        print("hello", self.__data['profiles'][self.user_id]['profile']['name'])
