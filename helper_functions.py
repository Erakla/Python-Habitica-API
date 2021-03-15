import time

def unix_to_timestamp(value: float):
    # "2021-03-10T23:00:00.000Z"
    return time.strftime("%%Y-%%m-%%dT%%H:%%M:%06.3fZ" % (value % 60), time.gmtime(value))

def timestamp_to_unix(timestamp: str):
    timezonedif = time.mktime(time.gmtime(86400)) - 86400
    localtimeseconds = time.mktime(time.strptime(timestamp[:-5], "%Y-%m-%dT%H:%M:%S"))
    ms = float(timestamp[-5:-1])
    return localtimeseconds + timezonedif + ms