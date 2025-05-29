
from src.tools.HTTP import *
from src.tools.MyRE import MyRE
from src.tools.MyList import MyList

class ChatGLM26B:

    def __init__(self, glm26bconf, log):

        self.conf = glm26bconf
        self.log = log

    def qes_gen(self, doc, qesgenconf):

        # 从doc 生成 qes

        body = {
            'prompt': qesgenconf.expend_qes_template.format(doc)
        }

        r = do_http_post(self.conf.url, body)

        print(r)

        a = r['response'].split_by_key('\n')

        if len(a) != qesgenconf.expend_num:
            print(f'------warn: len != {qesgenconf.expend_num} {a}')

        if len(a) < qesgenconf.expend_num:
            print(f'------err: len < {qesgenconf.expend_num} {a}')

        b = MyList.filter_by_list(a, ['', ' ', ' '])

        ret = []
        reg = r'^(问题)*\d[.:：]'

        for b_ in b:

            # 1. xxx -> xxx
            if MyRE.matched(reg, b_):
                c = MyRE.sub(reg, '', b_)
                ret.append(c)

        print(ret)
        return ret

    def resp_gen(self, qes, contexts):

        body = {
            'prompt': self.conf.edubrain_qa_template.format(contexts, qes)
        }

        self.log.info(body)

        r = do_http_post(self.conf.url, body)
        r = r['response']

        print(r)

        return r

    def trans(self, lst, idx):

        def call():

            r = do_http_post(self.conf.url[str(idx)], body)
            print(r)
            a = r['response'].split_by_key('\n')
            b = MyList.filter_by_list(a, ['', ' ', ' '])

            return b

        str_ = '请将下面这几句话分别翻译为英语，要求翻译后的英文中不能夹杂中文，每句英语独立一行：'
        for i, j in enumerate(lst):
            str_ += f'{i+1}. {j}\n'

        body = {
            'prompt': str_
        }

        b = call()

        num = 0
        while num < 3:
            if len(b) == len(lst):
                break

            b = call()

            num += 1

        if len(b) != len(lst):
            return [0] * len(lst)

        ret = []
        reg = r'^\d+[.:：][ ]*'

        for b_ in b:

            b_ = b_.strip()

            # 1. xxx -> xxx
            if MyRE.matched(reg, b_):
                c = MyRE.sub(reg, '', b_)
                ret.append(c)

            else:
                ret.append(b_)

        print(ret)

        return ret

