
from src.tools.HTTP import *
import re

class Qwen27B:

    def __init__(self, qwen27bconf, log):

        self.conf = qwen27bconf
        self.log = log

    def do_call(self, content):

        body = {
            'model': 'Qwen2-7B-Instruct',
            "temperature": 0.01,
            "top_p": 0.1,
            'messages': [
                {
                    'role': 'user',
                    'content': content
                }
            ]
        }

        self.log.info(body)

        # r = do_http_post(self.conf.url, body)

        # only for edubrain
        headers = {
            "Host": "inference-8.service.svc.cluster.local",
            "Content-Type": "application/json"
        }

        r = do_https_post(self.conf.url, body, headers=headers)

        r = r['choices'][0]['message']['content']

        self.log.info(r)

        return r

    def __call__(self, content, **kwargs):

        return self.do_call(content)


    def resp_gen(self, qes, contexts):

        answer = self.do_call(content=self.conf.edubrain_qa_template.format(contexts, qes))

        questions = []

        try:
            if not re.search(r"(抱歉|无法解答)", answer):
                questions = self.do_call(content=self.conf.edubrain_guess_template.format(contexts, qes))
                questions = eval(questions)

        except Exception as e:
            self.log.warn(e)

        return answer, questions
