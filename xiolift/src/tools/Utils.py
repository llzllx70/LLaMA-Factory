import uuid
from src.tools.PWException import *

def check_keys(need_keys, keys):
    for need_key in need_keys:
        if need_key not in keys:
            raise PWException(f'{need_key} not found')


def check_keys_with_len(need_keys, json_, len_=1):
    for need_key in need_keys:
        if need_key not in json_.keys():
            raise PWException(f'{need_key} not found')

        if len(json_[need_key]) < len_:
            raise PWException(f'len {need_key} < {len_}')


def check_keys_with_type_and_len(need_keys, json_, type_=str, len_=1):
    for need_key in need_keys:
        if need_key not in list(json_.keys()):
            raise PWException(f'{need_key} not found')

        if type(json_[need_key]) != type_:
            raise PWException(f'{need_key} type error')

        if len(json_[need_key]) < len_:
            raise PWException(f'len {need_key} < {len_}')

def build_args(port):

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=port, type=str)
    args = parser.parse_args()

    return args

def value_or_none(dict_, key_):

    if not dict_:
        return None

    if key_ in dict_.keys():
        return dict_[key_]

    return None

def value_or_default(dict_, key_, default=None):

    if not dict_:
        return default

    if key_ in dict_.keys():
        return dict_[key_]

    return default


def short_uuid():
    uuidChars = ("a", "b", "c", "d", "e", "f",
                 "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                 "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
                 "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
                 "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                 "W", "X", "Y", "Z")

    uuid_ = str(uuid.uuid4()).replace('-', '')
    result = ''
    for i in range(0, 8):
        sub = uuid_[i * 4: i * 4 + 4]
        x = int(sub, 16)
        result += uuidChars[x % 0x3E]
    return result
