from config.header import *
from tools.Json import Json

class Keyword:

    def __init__(self):
        # self.keywords = Json.load(f'../../data/kw_fasthan.docs_2_json')
        self.keywords = Json.load(f'{project_path}/out/kw_fasthan.json')

    def sort(self, words, top_k=90):

        ret = {}

        for word in words:
            if word in self.keywords.keys():
                ret[word] = self.keywords[word]

        # [('e', 3), ('d', 1)]
        d = sorted(ret.items(), key=lambda item: item[1], reverse=True)[20:top_k]

        ret_ = []
        for k, v in d:
            ret_.append(k)

        return ret_



