import json
from .Account import Account
import os

class Client:
    def __init__(self, author_uid: str, application_name: str, sendmsgdelay: int = 30, savelocation: str = "savedata", cachingdelay: int = 300):
        self.cachingdelay = cachingdelay
        self.author_uid = author_uid
        self.application_name = application_name
        self.sendmsgdelay = sendmsgdelay
        self.savelocation = savelocation
        self.profiles = {}
        self.groups = {}

    def connect(self, user_id: str, api_token: str) -> Account:
        return Account("%s-%s" % (self.author_uid, self.application_name), user_id, api_token, self.profiles, self.groups, self.sendmsgdelay, self.savelocation)

