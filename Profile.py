import HabiticaAPI.SendQueue as SendQueue
import HabiticaAPI.Exceptions as Exceptions
import HabiticaAPI.Group as Group
import time


class ProfileListIter:
    def __init__(self, data: dict, profile_ids: list):
        self.__data = data
        self._profile_ids = profile_ids
        self.__index = 0

    def __next__(self):
        self.__index += 1
        try:
            return Profile(self.__data, self._profile_ids[self.__index - 1])
        except IndexError:
            raise StopIteration

class ProfileList:
    def __init__(self, data: dict, profile_ids: list, group: Group.Group = None):
        self.__data = data
        self.ids = profile_ids
        self.__group = group

    def __iter__(self):
        if self.__group:
            self.__group.refresh_members_profiles()
        return ProfileListIter(self.__data, self.ids)

    def __getitem__(self, item):
        return Profile(self.__data, self.ids[item])

    def __len__(self):
        return len(self.ids)

class Profile:
    def __init__(self, data: dict, user_id: str):
        self.__data = data
        self.__user_id = user_id
        if self.__user_id in self.__data['profiles']:
            self.__profile = self.__data['profiles'][self.__user_id]
        else:
            self.__profile = None

    def refresh(self, forced: bool = False):
        if self.__user_id == self.__data['acc'].user_id:
            updateurl = 'api/v3/user'
        else:
            updateurl = 'api/v3/members/%s' % self.__user_id

        # if not assigned, load and assign
        if not self.__profile:
            self.__data['profiles'][self.__user_id] = self.__data['send']('get', updateurl, False)
            self.__profile = self.__data['profiles'][self.__user_id]
        # if not topical... load and update
        elif time.time() - self.__data['profiles'][self.__user_id]['synctime'] > self.__data['cached_duration'] \
                or time.time() - self.__profile.get('authenticatedProfileSynctime', 0) > self.__data['cached_duration']  \
                or forced:
            self.__profile.update(self.__data['send']('get', updateurl, False))
        else:
            return self
        self.__profile['synctime'] = time.time()
        if self.__user_id == self.__data['acc'].user_id:
            self.__profile['authenticatedProfileSynctime'] = time.time()
        return self

    def __refresh(func):
        def inner(self, *args, **kwargs):
            try:
                self.refresh()
            except Exceptions.ArgumentsNotAccepted as ex:
                raise Exceptions.InvalidID(ex, type_='user_id', id=self.__user_id)
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
    @__refresh
    def party(self):
        return Group.Group(self.__data, self.__profile['party']['_id'])

    def get_groups(self, type_: str, paginate: bool = None, page: int = None, queued: bool = True, callback: object = None):
        url = f'api/v3/groups?type={type_}'
        if paginate is not None:
            url += f"&paginate={['false', 'true']}"
            if page:
                url += f"&page={page}"
        return self.__data['send']('get', url, queued, callback)
