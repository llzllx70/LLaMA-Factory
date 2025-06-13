import json.decoder
import math
import re
import docx

from src.wrap.CwsWrap import CWSWrap

import glob
from src.tools.Json import *
from src.config.stops import stops

import jieba

class TFIDF:

    def __init__( 
        self, 
        file_dir,
        base_dir,
        algorithm='bm25'
    ):

        self.algorithm = algorithm
        self.dir = file_dir

        self.doc_words_f = f'{base_dir}/doc_words.json'
        self.idf_num_f = f'{base_dir}/idf_num.json'
        self.idf_f = f'{base_dir}/idf.json'

        self.files = []
        self.doc_words = []
        self.idf_num = {}
        self.idf = {}

    @staticmethod
    def is_word_and_num(ss):

        pattern = re.compile(r'^[a-zA-Z0-9]+$')

        result = pattern.match(ss)
        if result:
            return True
        else:
            return False

    def is_float(self, ss):

        try:
            if ss.find('%') != -1:
                return True

            if self.is_word_and_num(ss):
                return True

            float(ss)
            return True

        except Exception as e:
            return False

    def run(self):

        self.files =  sorted(glob.glob(os.path.join(self.dir, '*')))

        """
        加载所有doc到一个列表中, 同时完成分词
        self.doc_words = [
            [w1, w2],
            [w2, w3]
        ]
        """

        # self.load_docs_and_cws()

        """
        遍历列表，统计idf, 即每个单词在多少篇文章中出现
        self.idf_num = {
            'w1': 1,
            'w2': 2,
            'w3': 1
        }
        """

        # self.build_idf_num()

        """
        统计每个词的idf 值
        
        self.idf = {
            'w1': 3.4,
            'w2': 1.2,
            'w3': 3.4
        }
        """

        self.build_idf()

    @staticmethod
    def print(json_, flag, indent=2):
        flag = f'------------{flag}---------------'
        j = f'{flag}\n{json.dumps(json_, ensure_ascii=False, indent=indent)}\n'
        print(j)

    @staticmethod
    def load_json(file, ret=None):
        # print('begin load_json from {}'.format(file))
        if os.path.exists(file):
            with open(file, mode='r') as f:
                return json.load(f)

        if not ret:
            return {}
        return ret


    def load_docs_and_cws(self):

        def ff(v):
            # if self.is_float(v) or v in stops:
            if v in stops:
                return False
            return True

        j = 0
        for i, f in enumerate(self.files):

            print(f'load docs: {i} {f}')

            a = []

            with open(f, mode='r', encoding='utf-8') as f:
                try:
                    text = f.read()
                    r = self.split_strip_query(text)

                    for r_ in r:
                        if len(r_) > 0:
                            a += jieba.lcut(r_)

                    s = list(set(a))
                    b = list(filter(ff, s))
                    self.doc_words.append(b)

                except Exception as e:
                    print(f'error: {e}') 

        Json.save(f'{self.doc_words_f}', self.doc_words)

    def build_idf_num(self):

        for words in self.doc_words:
            for w in words:
                if w not in self.idf_num.keys():
                    self.idf_num[w] = 1
                else:
                    self.idf_num[w] += 1

        self.print(self.idf_num, 'idf_num')
        Json.save(self.idf_num_f, self.idf_num)

    def build_idf(self):
        """
        {
            'x': 0.3,
            'y': 0.5,
        }
        """
        doc_words = Json.load(self.doc_words_f)

        idf_num = Json.load(self.idf_num_f)

        doc_num = len(doc_words)

        t = {}

        for (k, v) in idf_num.items():

            if self.algorithm == 'tf-idf':
                arg = doc_num / v
                t[k] = round(math.log(arg), 4)

            elif self.algorithm == 'bm25':
                arg = (doc_num - v + 0.5) / (v + 0.5)
                t[k] = round(math.log(1 + arg), 4)  # add 1 是防止log后出现负数

        d = sorted(t.items(), key=lambda item: item[1], reverse=True)
        print(d)

        for k, v in d:
            self.idf[k] = v

        self.print(t, 'idf')
        Json.save(self.idf_f, self.idf)

    def find_kw(self, t1):

        kw = self.load_json(self.idf_f)

        ll = self.cws.run(t1)

        sort_ = {}

        print(t1)
        for w in ll:
            if w in kw.keys():
                sort_[w] = kw[w]

        d = sorted(sort_.items(), key=lambda item: item[1], reverse=True)
        # print(d[0:10])

        return d[0:10]

    @staticmethod
    def split_strip_query(query):

        split_flag = '[;；。?？!！﹔\n]'  # 句号分割

        # query = 'dkdkd。咕咕。'
        cc = re.split(split_flag, query)

        ret_ = []
        for tmp in cc:
            tmp = tmp.strip()
            if len(tmp) > 0:
                ret_.append(tmp)

        return ret_

    def doc_2_list(self, f, i):

        ret = []

        doc = docx.Document(f'./data/验证数据/{f}')

        for p in doc.paragraphs:
            r = self.split_strip_query(p.text)
            ret += r

        # self.print(ret, 'doc_2_list')

        kw = {}
        for ret_ in ret:

            d = self.find_kw(ret_)

            t = {}
            for k, v in d:
                t[k] = v

            kw[ret_] = t

        self.print(kw, f)

        Json.save(f'keyword_{f}.json', kw)

    def batch_test(self):

        fs = [
            '北京大学2021年强基计划招生简章.docx',
            '关于暑假期间进一步推进就业工作的通知.docx',
            '公开招聘事业编制工作人员公告.docx'
        ]

        for i, f in enumerate(fs):
            self.doc_2_list(f, i)


idf = TFIDF(
    file_dir='/home/xinghuo/PycharmProjects/xiolift/multi_doc_search/data/xiolift_1227/txt',
    base_dir='/home/xinghuo/PycharmProjects/xiolift/multi_doc_search/data/xiolift_1227/tfidf'
)

idf.run()

# idf.batch_test()

# exit(0)

t1 = [
    '考生高考成绩达到所在省份本科一批录取最低控制分数线（合并录取批次省份以各省 份划定分数线为准），且高考成绩达到我校在该省份强基计划招生入围标准。',
    '暑假期间，学校将持续开展不间断就业服务，每周一早上为固定值班时间，为有需要的毕业生办理盖章业务。',
    '温州大学是浙南闽北赣东区域唯一的综合性大学、浙江省重点建设高校、博士学位授予单位'
]

# for t in t1:
#     idf.find_kw(t)

# idf.batch_test()
