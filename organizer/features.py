import datetime

def extract_features(fname, size, mod_time):
    ext = fname.split('.')[-1].lower()
    ext_len = len(ext)
    name_len = len(fname)
    hour = mod_time.hour
    weekday = mod_time.weekday()
    return [size, name_len, ext_len, hour, weekday]