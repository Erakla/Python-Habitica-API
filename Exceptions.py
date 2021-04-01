class ArgumentsNotAccepted(BaseException):
    def __init__(self, callback, used_method, sent_data, rsp_dict, response):
        self.rsp_dict = rsp_dict
        self.sent_data = sent_data
        self.used_method = used_method
        self.callback = callback
        self.response = response
        self.message = rsp_dict['message']

    def __str__(self):
        return "%s: %s" % (self.rsp_dict['error'], self.rsp_dict['message'])

    def __call__(self, *args, **kwargs):
        return self.callback(False, *args, **kwargs)

class BadResponseFormat(BaseException):
    def __init__(self, response, callback, used_method, sent_data, ex):
        self.response = response
        self.callback = callback
        self.used_method = used_method
        self.senddata = sent_data
        self.raisedException = ex

    def __str__(self):
        return str(self.raisedException)

    def __call__(self, *args, **kwargs):
        return self.callback(False, *args, **kwargs)

class InvalidID(ArgumentsNotAccepted):
    def __init__(self, ex: ArgumentsNotAccepted, type_: str, id: str):
        self.id = id
        self.type = type_
        self.super = ex
        self.message = 'invalid id of type %s' % type_

class NotAuthorized(BaseException):
    def __init__(self, callback, used_method, sent_data, rsp_dict, response):
        self.rsp_dict = rsp_dict
        self.sent_data = sent_data
        self.used_method = used_method
        self.callback = callback
        self.response = response
        self.message = rsp_dict['message']

    def __str__(self):
        return "%s: %s" % (self.rsp_dict['error'], self.rsp_dict['message'])

    def __call__(self, *args, **kwargs):
        return self.callback(False, *args, **kwargs)