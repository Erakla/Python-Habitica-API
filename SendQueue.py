import requests
import json
import time
import threading

class SendQueue:
    def __init__(self, header: dict, delay: int = 30):
        self.base_url = "https://habitica.com/"
        self.header = header
        self.queue = []
        self.sender = threading.Thread(target=self._run)
        self.lastrequesttime = 0
        self.delay = delay

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
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
                continue
            self._send(self.queue.pop(0))

    def _send(self, msg):
        self.lastrequesttime = time.time()
        if msg['queued']:
            r = requests.request(msg['method'], url=self.base_url + msg['url'], json=msg['data'], headers=self.header)
            if r.status_code == 429:  # too many requests (http://habitica.fandom.com/wiki/Guidance_for_Comrades)
                self.queue.insert(0, msg)
                return
            if msg['callback']:
                try:
                    msg['callback'](**json.loads(r.text))
                except json.decoder.JSONDecodeError:
                    msg['callback'](r.text)
        else:
            while True:
                r = requests.request(msg['method'], url=self.base_url+msg['url'], json=msg['data'], headers=self.header)
                if r.status_code == 429:  # too many requests (http://habitica.fandom.com/wiki/Guidance_for_Comrades)
                    sek = float(r.headers['Retry-After'])
                    print("have %f secs to wait..." % sek)
                    time.sleep(sek)
                    continue
                else:
                    try:
                        return json.loads(r.text)
                    except json.decoder.JSONDecodeError:
                        return r.text
