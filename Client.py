from .Account import Account
import json
import os
import time

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        groups_file = os.path.join(self.savelocation, 'groups.json')
        remaining_data = {}
        for elem in self.data['groups']:
            # noinspection PyTypeChecker
            if time.time() - self.data['groups'][elem]['synctime'] < self.data['cached_duration']:
                remaining_data[elem] = self.data['groups'][elem]
        with open(groups_file, 'wt') as file:
            json.dump(self.data['groups'], file)

        profiles_file = os.path.join(self.savelocation, 'profiles.json')
        remaining_data = {}
        for elem in self.data['profiles']:
            # noinspection PyTypeChecker
            if time.time() - self.data['profiles'][elem]['synctime'] < self.data['cached_duration']:
                remaining_data[elem] = self.data['profiles'][elem]
        with open(profiles_file, 'wt') as file:
            json.dump(self.data['profiles'], file)

        objects_file = os.path.join(self.savelocation, 'objects.json')
        with open(objects_file, 'wt') as file:
            json.dump(self.data['objects'], file)

    def __enter__(self):
        groups_file = os.path.join(self.savelocation, 'groups.json')
        if os.path.exists(groups_file):
            with open(groups_file, 'rt') as file:
                self.data['groups'] = json.load(file)
        else:
            self.data['groups'] = {}

        profiles_file = os.path.join(self.savelocation, 'profiles.json')
        if os.path.exists(profiles_file):
            with open(profiles_file, 'rt') as file:
                self.data['profiles'] = json.load(file)
        else:
            self.data['profiles'] = {}

        objects_file = os.path.join(self.savelocation, 'objects.json')
        if os.path.exists(objects_file):
            with open(objects_file, 'rt') as file:
                self.data['objects'] = json.load(file)
        else:
            self.data['objects'] = {'appVersion': ''}
        return self

    def connect(self, user_id: str, api_token: str) -> Account:
        return Account(self.data, user_id, api_token)

