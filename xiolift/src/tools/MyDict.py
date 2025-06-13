
from collections import defaultdict
from src.tools.MyList import MyList
from src.tools.MyRandom import MyRandom


class MyDict:

    def __init__(self, dict_=None):

        if dict_:
            self.dict = dict_
        else:
            self.dict = defaultdict(dict)

    def items(self):
        return self.dict.items()

    def add_k_v(self, k, v):
        self.dict[k] = v

    def add_k_lv(self, k, v):
        """{'k': [v]}"""

        if self.has_k(k):
            self.dict[k].append(v)

        else:
            self.dict[k] = [v]

    def add_k_k_v(self, k1, k2, v):
        self.dict[k1][k2] = v

    def has_k(self, k):
        return k in self.dict.keys()

    def has_k_k(self, k1, k2):
        if k1 not in self.dict.keys():
            return False

        if k2 not in self.dict[k1].keys():
            return False

        return True

    def query_v_by_k(self, k, ret=None):

        if self.has_k(k):
            return self.dict[k]

        return ret

    def query_v_by_k_k(self, k1, k2):

        if not self.has_k_k(k1, k2):
            return self.dict[k1][k2]

        return None

    def update_by_k(self, k, v):

        if not self.has_k(k):
            return None

        self.dict[k] = v

    def query_k_by_interval(self, idx):

        for name, interval in self.dict.items():
            if interval[0] <= idx <= interval[1]:
                return name

        return ''

    def keys(self, deny=None):

        ks = list(self.dict.keys())

        l2 = [deny] if deny else []

        return MyList.filter_by_list(ks, list2=l2)

    def values(self, deny=None):

        ok_key = self.keys(deny=deny)

        values = []
        for k in ok_key:
            values += list(self.query_v_by_k(k, ret=[]))

        return values

    def random_keys(self, num):

        save_keys = list(self.dict.keys())
        MyRandom.shuffle(save_keys)

        return save_keys[0:num]

    def cut(self, num):

        # 取前面num个key，其它不要
        first_keys = list(self.dict.keys())[:num]
        first_dict = {k: self.dict[k] for k in first_keys}

        return first_dict



