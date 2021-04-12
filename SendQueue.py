import HabiticaAPI.Exceptions as Exceptions
import HabiticaAPI.helper_functions as hf
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

    def __call__(self, method: str, url: str, queued: bool = True, callback: object = None, data: dict = None, update: dict = None):
        msg = {
            'method': method,
            'url': url,
            'callback': callback,
            'queued': queued,
            'data': data,
            'update': update
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

    def refresh_objects(self, version: str):
        if not version or self.data['objects']['appVersion'] != version:
            url = 'api/v3/content?language=%s' % self.data['language']
            if version == '':
                self.data['objects']['appVersion'] = 'pass'
                objects = self.__call__('get', url, False)
                version = self.data['objects']['appVersion']
                self.data['objects'] = objects
            elif self.data['objects']['appVersion'] == 'pass':
                self.data['objects']['appVersion'] = version
                return
            else:
                self.data['objects']['appVersion'] = version
                self.data['objects'] = self.__call__('get', url, False)
            self.data['objects']['appVersion'] = version
            objects_file = os.path.join(self.data['savelocation'], 'objects.json')
            with open(objects_file, 'wt') as file:
                json.dump(self.data['objects'], file)

    def _log(self, logfolder, r):    # log
        logline = f"%-4d %-5s %-80s" % (r.status_code, r.request.method, r.request.url)
        if 300 <= r.status_code < 500:
            rdict = r.json()
            logline += "%s: %s" % (rdict['error'], rdict['message'])
        filename = f"{time.strftime('%Y-%m-%d')}.txt"
        os.makedirs(logfolder, exist_ok=True)
        with open(os.path.join(logfolder, filename), "at", encoding='utf8') as file:
            timestr = time.strftime("%H:%M:%S.")+("%.3f" % (time.time() % 1))[2:]
            file.write(f"{timestr} -- {logline}\n")

    def _send(self, msg):
        if msg['queued']:
            self.lastrequesttime = time.time()
            r = requests.request(msg['method'], url=self.base_url + msg['url'], json=msg['data'], headers=self.header)
            if self.data['logfolder']:
                self._log(self.data['logfolder'], r)
            if 200 <= r.status_code < 300:
                rdict = {}
                try:
                    rdict = r.json()
                    self.refresh_objects(rdict['appVersion'])
                    data = rdict['data']
                    if msg['update']:
                        self._update(msg['update'], rdict)
                    if msg['callback']:
                        return msg['callback'](success=True, status=r.status_code, data=data)
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
                if self.data['lazymode']:
                    while True:
                        elapsed = time.time() - self.lastrequesttime
                        if elapsed < self.data['sendmsgdelay']:
                            time.sleep(self.data['sendmsgdelay'] - elapsed)
                        else:
                            break
                self.lastrequesttime = time.time()
                r = requests.request(msg['method'], url=self.base_url+msg['url'], json=msg['data'], headers=self.header)
                if self.data['logfolder']:
                    self._log(self.data['logfolder'], r)
                if 200 <= r.status_code < 300:
                    try:
                        rdict = r.json()
                        self.refresh_objects(rdict['appVersion'])
                        data = rdict['data']
                        if msg['update']:
                            self._update(msg['update'], data)
                        return data
                    except json.JSONDecodeError as ex:
                        raise Exceptions.BadResponseFormat(r, msg['callback'], msg['method'], msg['data'], ex)
                    except KeyError as ex:
                        raise Exceptions.BadResponseFormat(r, msg['callback'], msg['method'], msg['data'], ex)
                if r.status_code == 429:  # too many requests (http://habitica.fandom.com/wiki/Guidance_for_Comrades)
                    sek = float(r.headers['Retry-After'])
                    if self.data['print_status_info']:
                        print("have %.2f secs to wait..." % sek)
                    time.sleep(sek)
                    continue
                else:
                    try:
                        rdict = r.json()
                        if rdict.get('error', '') == 'NotAuthorized':
                            raise Exceptions.NotAuthorized(msg['callback'], msg['method'], msg['data'], rdict, r)
                        raise Exceptions.ArgumentsNotAccepted(msg['callback'], msg['method'], msg['data'], rdict, r)
                    except json.decoder.JSONDecodeError as ex:
                        raise Exceptions.BadResponseFormat(r, msg['callback'], msg['method'], msg['data'], ex)

    def _update_chat_single_message(self, group_id, data: dict):
        message = data['message']
        message['timestamp'] = hf.timestamp_to_unix(message['timestamp'])
        chat = self.data['groups'][group_id]['chat']
        if chat[0]['timestamp'] < message['timestamp']:
            chat.insert(0, message)

    def _update(self, functions: dict, data: dict):
        update_functions = {
            'chatSingleMsg': self._update_chat_single_message
        }
        for func in functions:
            update_functions[func](functions[func], data)
