

from zhipuai import ZhipuAI

client = ZhipuAI(api_key="1d114cebd140de0c2ee5a5d1a7be66bd.WLFtqa81JJA2RJhR")



class ZhipuV2:

    def __init__(self):
        pass

    def run(self, message):

        response = client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=message
        )

        print(response.choices[0].message)
        return response.choices[0].message.content
