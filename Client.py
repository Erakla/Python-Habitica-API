from .Account import Account
import json
import os
import time

class Client:
    def __init__(self, author_uid: str, application_name: str, sendmsgdelay: int = 30, savelocation: str = "savedata",
                 cached_duration: int = 600, print_status_info=True, language: str = 'en'):
        """

        :param author_uid:
        :param application_name:
        :param sendmsgdelay:
        :param savelocation:
        :param cached_duration:
        :param print_status_info:
        :param language: Language code used for the items' strings. If the authenticated user makes the request, the content will return with the user's configured language.
                         default: "en"
                         allowed: "bg", "cs", "da", "de", "en", "en@pirate", "en_GB", "es", "es_419", "fr", "he", "hu", "id", "it", "ja", "nl", "pl", "pt", "pt_BR", "ro", "ru", "sk", "sr", "sv", "uk", "zh", "zh_TW"
        """
        self.data = {
            'author_uid': author_uid,
            'application_name': application_name,
            'cached_duration': cached_duration,
            'sendmsgdelay': sendmsgdelay,
            'print_status_info': print_status_info,
            'language': language,
            'savelocation': savelocation
        }

    def __enter__(self):
        groups_file = os.path.join(self.data['savelocation'], 'groups.json')
        if os.path.exists(groups_file):
            with open(groups_file, 'rt') as file:
                self.data['groups'] = json.load(file)
        else:
            self.data['groups'] = {}

        profiles_file = os.path.join(self.data['savelocation'], 'profiles.json')
        if os.path.exists(profiles_file):
            with open(profiles_file, 'rt') as file:
                self.data['profiles'] = json.load(file)
        else:
            self.data['profiles'] = {}

        objects_file = os.path.join(self.data['savelocation'], 'objects.json')
        if os.path.exists(objects_file):
            with open(objects_file, 'rt') as file:
                self.data['objects'] = json.load(file)
        else:
            self.data['objects'] = {'appVersion': ''}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        groups_file = os.path.join(self.data['savelocation'], 'groups.json')
        remaining_data = {}
        for elem in self.data['groups']:
            # noinspection PyTypeChecker
            if time.time() - self.data['groups'][elem]['synctime'] < self.data['cached_duration']:
                remaining_data[elem] = self.data['groups'][elem]
        with open(groups_file, 'wt') as file:
            json.dump(self.data['groups'], file)

        profiles_file = os.path.join(self.data['savelocation'], 'profiles.json')
        remaining_data = {}
        for elem in self.data['profiles']:
            # noinspection PyTypeChecker
            if time.time() - self.data['profiles'][elem]['synctime'] < self.data['cached_duration']:
                remaining_data[elem] = self.data['profiles'][elem]
        with open(profiles_file, 'wt') as file:
            json.dump(self.data['profiles'], file)

    def connect(self, user_id: str, api_token: str) -> Account:
        return Account(self.data, user_id, api_token)

