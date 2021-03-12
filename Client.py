import json
from .Account import Account
import os

class Client:
    def __init__(self, author_uid: str, application_name: str, sendmsgdelay: int = 30, savelocation: str = "savedata",
                 cached_duration: int = 600, print_status_info=True):
        self.savelocation = savelocation
        self.data = {
            'author_uid': author_uid,
            'application_name': application_name,
            'cached_duration': cached_duration,
            'sendmsgdelay': sendmsgdelay,
            'print_status_info': print_status_info
        }

        groups_file = os.path.join(savelocation, 'groups.json')
        if os.path.exists(groups_file):
            with open(groups_file, 'rt') as file:
                self.data['groups'] = json.load(file)
        else:
            self.data['groups'] = {}

        profiles_file = os.path.join(savelocation, 'profiles.json')
        if os.path.exists(profiles_file):
            with open(profiles_file, 'rt') as file:
                self.data['profiles'] = json.load(file)
        else:
            self.data['profiles'] = {}

        objects_file = os.path.join(savelocation, 'objects.json')
        if os.path.exists(objects_file):
            with open(objects_file, 'rt') as file:
                self.data['objects'] = json.load(file)
        else:
            self.data['objects'] = {'appVersion': ''}

    def connect(self, user_id: str, api_token: str) -> Account:
        return Account(self.data, user_id, api_token)

