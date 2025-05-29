
import numpy as np
import struct

from config.header import *
from tools.Json import *
from config.stops import stops


class Cos:

    def __init__(self, weight=1, oov=None, keywords=None):

        self.weight = weight

        if keywords is None:
            self.keywords = Json.load(f'../../data/kw_fasthan.json')

        else:
            self.keywords = keywords

        self.dim = None
        self.w2v = {}

        self.load_w2v_bin(f'{project_path}/word2vec/vec.bin')

    def load_w2v_bin(self, w2v_f):

        with open(w2v_f, mode='rb') as f:

            words_num = bytes(0)
            c = f.read(1)
            while c != b' ':
                words_num += c
                c = f.read(1)

            dimension = bytes(0)
            c = f.read(1)
            while c != b'\n':
                dimension += c
                c = f.read(1)

            words_num = int(words_num)
            self.dim = int(dimension)

            index_ = 0

            while index_ < words_num:
                key = bytes(0)
                c = f.read(1)
                while c != b' ':
                    key += c
                    c = f.read(1)

                self.w2v[key.decode(encoding='utf-8')] = \
                    np.array(struct.unpack('f' * self.dim, f.read(4 * self.dim)))
                f.read(1)

                index_ += 1

    def run(self, q):

        b = np.zeros(self.dim, float)

        for i in q:
            if i not in stops:

                if i in self.w2v.keys():
                    if i in self.keywords.keys():
                        b += np.array(self.w2v[i]) * self.keywords[i]
                    else:
                        b += self.w2v[i]
                else:
                    b += self.w2v['</s>']

        c = np.sqrt(b.dot(b))

        if c == 0:
            print(q)

        return b / c

