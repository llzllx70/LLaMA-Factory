from random import shuffle
from src.tools.MyRandom import MyRandom
from src.tools.Json import Json
from src.tools.MyStr import MyStr
import itertools

class MyList:

    @staticmethod
    def filter(nodes, index, duplicate=False):

        ret, idx = [], []

        for i in index:

            # 允许重复
            if duplicate:
                ret.append(nodes[i])
                idx.append(i)

            # 不允许重复
            elif nodes[i] not in ret:
                ret.append(nodes[i])
                idx.append(i)

        return ret, idx

    @staticmethod
    def find_idx(list_, interval_):

        for i, j in enumerate(list_):
            if j == interval_:
                return i

        return -1

    def filter_by_idx(self, l1, l2, f):
        pass

    @staticmethod
    def merge_list_by_len(list_, len_):

        ret = []
        this = list_[0]

        for s in list_[1:]:

            if len(this) + len(s) >= len_:

                ret.append(this)
                this = s

            else:
                this += s

        if len(this) > 0:
            ret.append(this)

        return ret

    @staticmethod
    def filter_by_list(list1, list2):

        r = []

        for i in list1:
            if i not in list2:
                r.append(i)

        return r

    @staticmethod
    def get_col(llist, col_idx):

        # [[1, 2], [3, 4]] -> [1, 3]  or [2, 4]
        b = [l[col_idx] for l in llist]

        return b

    @staticmethod
    def iter(list_, step_=10):

        for i in range(0, len(list_), step_):
            yield list_[i:i+step_]

    @staticmethod
    def split_by_len(list_, len_):

        i0 = list_[0][0:len_]
        ret = [i0]
        total = len(i0)

        for i in list_[1:]:

            if len(i) + total > len_:
                break

            else:
                ret.append(i)
                total += len(i)

        return ret

    @staticmethod
    def remove_first_item(list_, item_):

        if item_ in list_:
            list_.remove(item_)

    @staticmethod
    def random_value(list_, num=None, deny=None):

        a = list_[:]

        if deny:
            MyList.remove_first_item(a, deny)

        shuffle(a)

        if num:
            return a[0:num]

        else:
            return a

    @staticmethod
    def random_split(list_, rate=0.2):

        a = MyList.random_value(list_)

        len1 = int(len(a) * rate)

        return a[0:len1], a[len1:]

    @staticmethod
    def split_by_chunk(lst, chunk_size):
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @staticmethod
    def split_by_part(lst, part_num):

        a = len(lst) // part_num
        b = len(lst) % part_num

        chunk_size = a if b == 0 else a + 1

        return MyList.split_by_chunk(lst, chunk_size)

    @staticmethod
    def split_by_rate3(lst, rate):
        # rate: [0.8, 0.1, 0.1]

        len_ = len(lst)

        e1 = int(len_ * rate[0])
        e2 = int(len_ * rate[0] + len_ * rate[1])

        s1 = lst[0:e1]
        s2 = lst[e1:e2]
        s3 = lst[e2:]

        return s1, s2, s3

    @staticmethod
    def split_by_dict(list_, split_info):
        """
        split_info = {

            'json_train': {
                'rate': [0, 0.8],
                'data': f'{base_dir}/train.json',
            },

            'json_test_pos': {
                'rate': [0.8, 0.9],
                'data': f'{base_dir}/test_pos.json',
            },

            'json_test_neg': {
                'rate': [0.9, 1.0],
                'data': f'{base_dir}/test_neg.json'
            }
        }
        """

        len_ = len(list_)
        idx = [i for i in range(len_)]
        MyRandom.shuffle(idx)

        ret = []

        for k, v in split_info.items():
            b = int(v['rate'][0] * len_)
            e = int(v['rate'][1] * len_)

            idx_ = idx[b:e]

            file = v['data']

            this_list = [list_[k] for k in idx_]

            Json.save(file, this_list)
            ret.append(this_list)

        return ret

    @staticmethod
    def dim(lst, dim=0):

        return [i[dim] for i in lst]

    @staticmethod
    def delete(lst, beg, end):

        lst = list(itertools.chain(lst[:beg], lst[end:]))
        return lst

    @staticmethod
    def concat_ll(ll):

        """
        ll: [['xxx1', 'xxxx2'], ['yyy1', 'yyy2']]
        """

        str_ = ''
        for l in ll:
            for i in l:
                if i not in [None, 'None']:
                    str_ += str(i) + ' '

        return MyStr.to_plain(str_)












