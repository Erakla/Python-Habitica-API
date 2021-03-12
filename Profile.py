import time
from .SendQueue import SendQueue

class ProfileList(list):
    pass

class Profile:
    def __init__(self, data: dict, send: SendQueue, user_id: str):
        self.data = data
        self.send = send
        self.user_id = user_id

    @staticmethod
    def __reload(func):
        def inner(self, *args, **kwargs):
            if self.profile_id not in self.data['profiles'] or time.time() - self.data['profiles'][self.user_id]['synctime'] > self.data['cached_duration']:
                self.data['profiles'][self.profile_id] = self.send('get', 'api/v3/members/%s' % self.user_id, False)
            return func(self, *args, **kwargs)
        return inner