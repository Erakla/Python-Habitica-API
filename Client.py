import HabiticaAPI.Account as Account
import json
import os
import time

class Client:
    def __init__(self, author_uid: str, application_name: str, sendmsgdelay: int = 30, savelocation: str = "savedata",
                 cached_duration: int = 600, print_status_info=True, language: str = 'en', lazymode: bool = False, logfolder: str = None):
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
        :param lazymode: uses cached_duration also for requests in background i.e. refreshing of data before a call like profile[members]
        """
        self.data = {
            'author_uid': author_uid,
            'application_name': application_name,
            'cached_duration': cached_duration,
            'sendmsgdelay': sendmsgdelay,
            'print_status_info': print_status_info,
            'language': language,
            'savelocation': savelocation,
            'lazymode': lazymode,
            'logfolder': logfolder
        }
        self._accs = []

    def __enter__(self):
        if not os.path.exists(self.data['savelocation']):
            os.mkdir(self.data['savelocation'])

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
        for acc in self._accs:
            if acc.send.sender.is_alive():
                acc.send.sender.join()

        groups_file = os.path.join(self.data['savelocation'], 'groups.json')
        remaining_data = {}
        for id_ in self.data['groups']:
            # noinspection PyTypeChecker
            if time.time() - self.data['groups'][id_]['synctime'] < self.data['cached_duration']:
                remaining_data[id_] = self.data['groups'][id_]
        with open(groups_file, 'wt') as file:
            json.dump(self.data['groups'], file)

        profiles_file = os.path.join(self.data['savelocation'], 'profiles.json')
        remaining_data = {}
        for id_ in self.data['profiles']:
            # noinspection PyTypeChecker
            if time.time() - self.data['profiles'][id_]['synctime'] < self.data['cached_duration']:
                remaining_data[id_] = self.data['profiles'][id_]
        with open(profiles_file, 'wt') as file:
            json.dump(self.data['profiles'], file)

    def connect(self, user_id: str, api_token: str) -> Account.Account:
        self._accs.append(Account.Account(self.data, user_id, api_token))
        return self._accs[-1]

