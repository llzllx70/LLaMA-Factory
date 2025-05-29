

from src.tools.HTTP import *

class GLM49BChat:

    def __init__(self):
        self.url = 'http://172.16.2.49:1568/v1/chat/completions'

    def __call__(self, prompt, **kwargs):

        body = {
            'prompt': prompt
        }

        r = do_http_post(self.url, body)
        r = r['response']

        return r
