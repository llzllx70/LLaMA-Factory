
"""
视觉语言模型，用于内容提取等
"""
from src.tools.HTTP import do_http_post

import base64
from openai import OpenAI
import pdfplumber

prompt_eng = """Extract all content from the image Faithful. The requirements are as follows: 
1. Do not omit any information in the image, and do not add any extra information.
2. Do not include any repeated content in the output. 
3. The table should only output the content, without any additional formatting.
4. The maximum output length should not exceed 2000 characters.
"""

prompt_zh = """忠实地从图像中提取所有内容，要求如下：
1. 不要遗漏图中的任何信息，也不要添加额外的信息。
2. 输出中不要有重复的内容。
3. 表格只需输出内容，不需要其他格式。
4. 对表格后面的空行不要输出
5. 最大输出长度不超过2000个字符。
"""

prompt_qa = """从图中所提供的信息中概括性的提取重要的问题及该问题的答案
要求如下:
1. 要保证所提取问题的完整性，方便后续检索，对于出现设备型号的地方要带上
2. 问题和答案一定要成对出现
3. 问题要有一定的概括性， 问题的答案不少于50字
4. 对于图中出现的标题可作为问题，标题下的内容可作为答案
5. 一张图最多提取10个问题

以QA对的形式返回，如：

问题1： 8642如何调试?
答案: 调试过程为...

问题2： 8642状态查询
答案: 查询方式为...

"""

prompt = prompt_zh

class VisualLLMvllmQwen2:

    """
    以vllm方式启动的qwen2_vl_instruct-7b的入口
    """

    def __init__(self, log, api_key='EMPTY', api_base="http://172.16.2.18:8000/v1"):

        self.log = log

        self.openai_api_key = api_key
        self.openai_api_base = api_base

        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )

    def batch_infer(self, content):

        try:

            content.append({"type": "text", "text": prompt})

            chat_response = self.client.chat.completions.create(

                model="Qwen2.5-VL-7B-Instruct",
                messages=[
                    {
                        "role": "user",
                        "content": content
                    },
                ],
                temperature=0.01,
                top_p=0.01,  # 设置小，选择快，可加快速度
                max_tokens=2000,
            )

            content = chat_response.choices[0].message.content

            return content

        except Exception as e:

            self.log.warn(e)

            return f'[[None]]'


    def infer(self, image_path):

        try:

            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read())

            encoded_image_text = encoded_image.decode("utf-8")
            base64_qwen = f"data:image;base64,{encoded_image_text}"

            chat_response = self.client.chat.completions.create(

                model="Qwen2.5-VL-7B-Instruct",
                messages=[
                    # {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "system", "content": "You are a helpful OCR assistant."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": base64_qwen}},
                            # prompt 0
                            # {"type": "text", "text": "Extract all content from the image in detail and organize it into a more understandable format. The requirements are as follows: 1. If it's a table, convert it into Markdown table format. 2. If there are original numbered titles, retain the numbering. 3. Follow the original order of the text. 4. Do not repeatedly output invalid characters."}
                            # prompt 1
                            # {"type": "text", "text": "Extract all content from the image in detail and organize it into a more understandable format. The requirements are as follows: 1. If there are original numbered titles, retain the numbering. 2. Follow the original order of the text. 3. Do not include any repeated content in the output. 4. Do not omit any information in the image, and do not add any extra information."}
                            # prompt 2
                            {"type": "text", "text": prompt}
                        ],
                    },
                ],
                temperature=0.01,
                top_p=0.01,  # 设置小，选择快，可加快速度
                max_tokens=2000,
            )

            content = chat_response.choices[0].message.content
            self.log.info(f'{image_path} return\n{content}')

            return content

        except Exception as e:

            self.log.warn(e)

            return f'[[{image_path} None]]'


class VisualLLMQwen25VL:

    """
    调用qwen2.5_vl_service的入口, 7b
    """

    def __init__(self, log, url):

        self.log = log

        self.url = url

    def infer(self, image_path):

        try:

            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read())

            encoded_image_text = encoded_image.decode("utf-8")
            base64_qwen = f"data:image;base64,{encoded_image_text}"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": base64_qwen},
                        {"type": "text", "text": prompt_zh},
                    ],
                }
            ]

            ret = do_http_post(self.url, {'method': 'infer', 'messages': messages})

            if ret['code'] != 0:
                return f'[[{image_path} None]]'

            return ret['content']

        except Exception as e:

            self.log.warn(e)

            return f'[[{image_path} None]]'

class QwenVLApi:

    def __init__(self, log, model_name_or_path):

        self.client = OpenAI(
            api_key='3dee2593925641dc98bb16de1ce80938',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


    #  base 64 编码格式
    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def run(self, images):

        # images 是路径

        content = []

        for image in images:

            # 需要注意，传入Base64，图像格式（即image/{format}）需要与支持的图片列表中的Content Type保持一致。"f"是字符串格式化的方法。
            # PNG图像：  f"data:image/png;base64,{base64_image}"
            # JPEG图像： f"data:image/jpeg;base64,{base64_image}"
            # WEBP图像： f"data:image/webp;base64,{base64_image}"
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{self.encode_image(image)}"}
                }   
            )

        content.append({"type": "text", "text": prompt_zh})

        completion = self.client.chat.completions.create(
            model="qwen-vl-plus-2025-01-25",
            messages=[
                {
                    "role": "system",
                    "content": [{"type":"text","text": "You are a helpful assistant."}]},
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        print(completion.choices[0].message.content)
