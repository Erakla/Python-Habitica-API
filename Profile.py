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
    def __init__(self, data: dict, send: SendQueue.SendQueue, profile_ids: list, group: Group.Group = None):
        self.__data = data
        self.__send = send
        self.ids = profile_ids
        self.__group = group

    def __iter__(self):
        if self.__group:
            self.__group.refresh_members_profiles()
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
        if self.__user_id in self.__data['profiles']:
            self.__profile = self.__data['profiles'][self.__user_id]
        else:
            self.__profile = None

    def refresh(self):
        # if not assigned, load and assign
        if not self.__profile:
            self.__data['profiles'][self.__user_id] = self.__send('get', 'api/v3/members/%s' % self.__user_id, False)
            self.__profile = self.__data['profiles'][self.__user_id]
            self.__profile['synctime'] = time.time()
        # if not topical... load and update
        elif time.time() - self.__data['profiles'][self.__user_id]['synctime'] > self.__data['cached_duration']:
            self.__profile.update(self.__send('get', 'api/v3/members/%s' % self.__user_id, False))
            self.__profile['synctime'] = time.time()

    def __refresh(func):
        def inner(self, *args, **kwargs):
            try:
                self.refresh()
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

    def get_groups(self, type_: str, paginate: bool = None, page: int = None, queued: bool = True, callback: object = None):
        url = f'api/v3/groups?type={type_}'
        if paginate is not None:
            url += f"&paginate={['false', 'true']}"
            if page:
                url += f"&page={page}"
        return self.__send('get', url, queued, callback)
