import HabiticaAPI.Exceptions as Exceptions
import HabiticaAPI.Profile as Profile
import HabiticaAPI.Chat as Chat
import time

class GroupList:
    pass

class Group:
    def __init__(self, data: dict, group_id: str):
        self.__data = data
        self.__group_id = group_id
        if group_id in data['groups']:
            self.__group = self.__data['groups'][self.__group_id]
        else:
            self.__group = None

    def __refresh_group_member_entries(self):
        if time.time() - self.__group.get('members_synctime', 0) > self.__data['cached_duration']:
            query = f'api/v3/groups/{self.__group_id}/members?includeTasks=true'
            memberlist = []
            for i in range(0, self.__group['memberCount'], 30):
                if memberlist:
                    memberlist += self.__data['send']('get', f"{query}&lastId={memberlist[-1]['id']}", False)
                else:
                    memberlist = self.__data['send']('get', query, False)
            self.__group['members'] = memberlist
            self.__group['members_synctime'] = time.time()

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
                self.refresh()
            except Exceptions.ArgumentsNotAccepted as ex:
                raise Exceptions.InvalidID(ex, type_='group_id', id=self.__group_id)
            return func(self, *args, **kwargs)
        return inner

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
    def members(self):
        self.__refresh_group_member_entries()
        member_ids = [member['id'] for member in self.__group['members']]
        return Profile.ProfileList(self.__data, member_ids, self)

    # noinspection PyArgumentList
    @property
    @__refresh
    def chat(self):
        return Chat.Chat(self.__data, self.__group_id)

    def refresh_members_profiles(self):
        expired = 0
        for member in self.__group['members']:
            if member['id'] not in self.__data['profiles']:
                expired += 1
            elif time.time() - self.__data['profiles'][member['id']]['synctime'] > self.__data['cached_duration']:
                expired += 1
        if expired > self.__group['memberCount']/30+1:
            query = f'api/v3/groups/{self.__group_id}/members?includeTasks=true&includeAllPublicFields=true'
            memberlist = []
            for i in range(0, self.__group['memberCount'], 30):
                if memberlist:
                    memberlist += self.__data['send']('get', f"{query}&lastId={memberlist[-1]['id']}", False)
                memberlist = self.__data['send']('get', query, False)
            for member in memberlist:
                member['synctime'] = time.time()
                if member['id'] not in self.__data['profiles']:
                    self.__data['profiles'][member['id']] = member
                else:
                    self.__data['profiles'][member['id']].update(member)
