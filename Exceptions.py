class ArgumentsNotAcceptedException(BaseException):
    def __init__(self, error, message, callback, response):
        self.message = message
        self.error = error
        self.callback = callback
        self.response = response

    def __str__(self):
        return "%s: %s" % (self.error, self.message)

    def __call__(self, *args, **kwargs):
        return self.callback(False, *args, **kwargs)

class BadResponseFormatException(BaseException):
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
