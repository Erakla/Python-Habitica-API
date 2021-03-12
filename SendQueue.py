from .Exceptions import ArgumentsNotAcceptedException, BadResponseFormatException
import requests
import json
import time
import threading
import os

class SendQueue:
    def __init__(self, data, header: dict):
        self.data = data
        self.base_url = "https://habitica.com/"
        self.header = header
        self.queue = []
        self.sender = threading.Thread(target=self._run)
        self.lastrequesttime = 0
        self.errorlog = []

    def __call__(self, method: str, url: str, queued: bool = True, callback: object = None, data: dict = None):
        msg = {
            'method': method,
            'url': url,
            'callback': callback,
            'queued': queued,
            'data': data
        }
        if queued:
            self.queue.append(msg)
            if not self.sender.is_alive():
                self.sender.start()
        else:
            return self._send(msg)

    def _run(self):
        while self.queue:
            elapsed = time.time() - self.lastrequesttime
            if elapsed < self.data['sendmsgdelay']:
                time.sleep(self.data['sendmsgdelay'] - elapsed)
                continue
            self._send(self.queue.pop(0))

    def _refresh_objects(self, version: str):
        if self.data['objects']['appVersion'] != version:
            url = 'api/v3/content?language=%s' % self.data['language']
            self.data['objects'] = self.__call__('get', url, False)
            self.data['objects']['appVersion'] = version

            objects_file = os.path.join(self.data['savelocation'], 'objects.json')
            with open(objects_file, 'wt') as file:
                json.dump(self.data['objects'], file)

    def _send(self, msg):
        self.lastrequesttime = time.time()
        if msg['queued']:
            r = requests.request(msg['method'], url=self.base_url + msg['url'], json=msg['data'], headers=self.header)
            if 200 <= r.status_code < 300:
                rdict = {}
                try:
                    rdict = r.json()
                    self._refresh_objects(rdict['appVersion'])
                    if msg['callback']:
                        return msg['callback'](success=True, status=r.status_code, data=rdict['data'])
                except json.JSONDecodeError as ex:
                    if msg['callback']:
                        msg['callback'](success=False, status=r.status_code, response=r, exception=ex)
                    else:
                        self.errorlog.append((msg, r))
                except KeyError as ex:
                    if msg['callback']:
                        msg['callback'](success=False, status=r.status_code, data=rdict, response=r, exception=ex)
                    else:
                        self.errorlog.append((msg, r))
            if r.status_code == 429:  # too many requests (http://habitica.fandom.com/wiki/Guidance_for_Comrades)
                self.queue.insert(0, msg)
            else:
                if msg['callback']:
                    msg['callback'](status=r.status_code, method=msg['method'], sent_body=msg['data'], request=r)
                else:
                    self.errorlog.append((msg, r))
        else:
            while True:
                r = requests.request(msg['method'], url=self.base_url+msg['url'], json=msg['data'], headers=self.header)
                if 200 <= r.status_code < 300:
                    try:
                        rdict = r.json()
                        self._refresh_objects(rdict['appVersion'])
                        return rdict['data']
                    except json.JSONDecodeError as ex:
                        raise BadResponseFormatException(r, msg['callback'], msg['method'], msg['data'], ex)
                    except KeyError as ex:
                        raise BadResponseFormatException(r, msg['callback'], msg['method'], msg['data'], ex)
                if r.status_code == 429:  # too many requests (http://habitica.fandom.com/wiki/Guidance_for_Comrades)
                    sek = float(r.headers['Retry-After'])
                    if self.data['print_status_info']:
                        print("have %f secs to wait..." % sek)
                    time.sleep(sek)
                    continue
                else:
                    try:
                        rdict = r.json()
                        raise ArgumentsNotAcceptedException(msg['callback'], msg['method'], msg['data'], rdict, r)
                    except json.decoder.JSONDecodeError as ex:
                        raise BadResponseFormatException(r, msg['callback'], msg['method'], msg['data'], ex)
