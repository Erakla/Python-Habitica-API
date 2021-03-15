import HabiticaAPI.SendQueue as SendQueue
import HabiticaAPI.Exceptions as Exceptions
import HabiticaAPI.Group as Group
import time


class ProfileListIter:
    def __init__(self, data: dict, send: SendQueue.SendQueue, profile_ids: list):
        self.__data = data
        self.__send = send
        self._profile_ids = profile_ids
        self.__index = 0

    def __next__(self):
        self.__index += 1
        try:
            return Profile(self.__data, self.__send, self._profile_ids[self.__index - 1])
        except IndexError:
            raise StopIteration

class ProfileList:
    def __init__(self, data: dict, send: SendQueue.SendQueue, profile_ids: list):
        self.__data = data
        self.__send = send
        self.ids = profile_ids

    def __iter__(self):
        return ProfileListIter(self.__data, self.__send, self.ids)

    def __getitem__(self, item):
        return Profile(self.__data, self.__send, self.ids[item])

    def __len__(self):
        return len(self.ids)

class Profile:
    def __init__(self, data: dict, send: SendQueue.SendQueue, user_id: str):
        self.__data = data
        self.__send = send
        self.__user_id = user_id
        self.__profile = None

    def __refresh(func):
        def inner(self, *args, **kwargs):
            try:
                # if not assigned
                if not self.__profile:
                    # but existant... assign
                    if self.__user_id in self.__data['profiles']:
                        self.__profile = self.__data['profiles'][self.__user_id]
                    else:  # or load and assign
                        self.__data['profiles'][self.__user_id] = self.__send('get', 'api/v3/members/%s' % self.__user_id, False)
                        self.__profile = self.__data['profiles'][self.__user_id]
                        self.__profile['synctime'] = time.time()
                # if not topical... load and update
                if time.time() - self.__data['profiles'][self.__user_id]['synctime'] > self.__data['cached_duration']:
                    self.__profile.update(self.__send('get', 'api/v3/members/%s' % self.__user_id, False))
                    self.__profile['synctime'] = time.time()
            except Exceptions.ArgumentsNotAcceptedException as ex:
                raise Exceptions.InvalidIDException(ex, type_='user_id', id=self.__user_id)
            return func(self, *args, **kwargs)
        return inner

    # noinspection PyArgumentList
    @__refresh
    def __getitem__(self, item):
        return self.__profile[item]

    # noinspection PyArgumentList
    @property
    @__refresh
    def content(self):
        return self.__profile

    @property
    def party(self):
        return Group.Group(self.__data, self.__send, self.__profile['party']['_id'])
