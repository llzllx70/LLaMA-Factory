
from src.ake.cus_exception import ApiError
from src.ake.glm_api import GLMApi
from src.tools.MyList import MyList
from src.tools.MyRE import MyRE


class Zhipu(GLMApi):

    def __init__(self, zhipuconf):
        super().__init__(model=zhipuconf.model_name)

        self.conf = zhipuconf

    def call_zhipu(self, prompt):

        r = self(
            prompt,
            model_params={
                "temperature": self.conf.temperature,
                "top_p": self.conf.top_p
            }
        )

        return r

    def qes_gen(self, doc, qesgen_conf):

        prompt = qesgen_conf.expend_qes_template.format(doc)

        r = self.call_zhipu(prompt)

        print(r)

        a = r.split_by_key('\n')

        if len(a) != qesgen_conf.expend_num:
            print(f'------warn: len != {qesgen_conf.expend_num} {a}')

        if len(a) < qesgen_conf.expend_num:
            print(f'------err: len < {qesgen_conf.expend_num} {a}')

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

    def resp_gen(self, qes, context_):

        try:
            prompt = self.conf.gen_resp_template.format(context_, qes)
            r = self.call_zhipu(prompt)

            return r

        except ApiError as e:
            return e.message

    def hyde_gen(self, qes, hyde_conf):

        try:
            prompt = hyde_conf.template.format(qes)
            r = self.call_zhipu(prompt)

            return r

        except ApiError as e:
            return e.message
