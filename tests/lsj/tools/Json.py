
import os
import json
import jsonlines
from .MyRandom import MyRandom
from .MyPath import MyPath


class Json:

    @staticmethod
    def load(file, ret=None):
        print('begin load_json from {}'.format(file))
        if os.path.exists(file):
            with open(file, mode='r') as f:
                return json.load(f)

        if not ret:
            return {}
        return ret

    @staticmethod
    def save(file, data, indent=2):
        MyPath().check_path(file)
        with open(file, mode='w') as f:
            js = json.dumps(data, ensure_ascii=False, indent=indent)
            f.write(js)
            f.close()

    @staticmethod
    def savel(file, data):

        """以jsonl的方式保存，注意不是保存列表"""

        MyPath().check_path(file)
        with jsonlines.open(file, mode='w') as f:
            for dict_ in data:
                f.write(dict_)
            f.close()

    @staticmethod
    def loadl(file):

        ret = []
        with open(file, "r+", encoding="utf8") as f:
            for item in jsonlines.Reader(f):
                ret.append(item)

            f.close()
            return ret

    @staticmethod
    def pretty(json_, indent=2):
        return json.dumps(json_, ensure_ascii=False, indent=indent)

    @staticmethod
    def print(json_, flag='out', indent=2):
        flag = f'------------{flag}---------------'
        pretty_str = Json.pretty(json_, indent=indent)
        j = f'{flag}\n{pretty_str}\n'

        print(j)

    @staticmethod
    def str_2_json(str_):
        a = json.loads(str_)
        return a

    @staticmethod
    def json_2_str(json_):
        return json.dumps(json_, ensure_ascii=False)

    @staticmethod
    def jsonstr_2_cleanstr(str_):
        return Json.json_2_str(Json.str_2_json(str_))

    @staticmethod
    def split_by_key(my_json, split_info, flat=False):

        keys = list(my_json.keys())
        len_ = len(keys)

        MyRandom.shuffle(keys)

        ret = []

        for k, v in split_info.items():
            b = int(v['rate'][0] * len_)
            e = int(v['rate'][1] * len_)

            ks = keys[b:e]

            file_ = v['data']

            if flat:
                data = []

                for i in ks:
                    j = my_json.query_v_by_k(i, ret=[])
                    for j_ in j:
                        data.append([j_, i])

            else:
                data = {}
                for k in ks:
                    data[k] = my_json.query_v_by_k(k, ret=[])

            print(f'{file_}: {len(data)}')
            Json.save(file_, data)

            ret.append(data)

        return ret
