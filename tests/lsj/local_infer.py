
import os
import json
import time
import base64
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://172.16.2.49:8002/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

PROMPT = """
图片是电梯各个部件的照片，目前有如下类别:
{types}
请识别当前图片属于哪个类别，只输出类别名称，不要输出其他信息。
"""


class XioLift:

    def __init__(self, img_dir):

        self.cwd = os.getcwd()

        self.model = "Qwen2.5-VL-7B-Instruct"

        self.img_dir = img_dir
        self.root_img_path = f'{self.cwd}/{img_dir}'
        self.structure = self.build_structure()
        self.prompt = self.build_prompt()


    def build_prompt(self):

        types = str(list(self.structure.keys()))
        return PROMPT.format(types=types)

    def dir_to_dict(self, path):
        result = {}
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result[item] = self.dir_to_dict(full_path)
            else:
                # 当前目录就是叶子目录，直接用目录名映射文件名列表
                return sorted(os.listdir(path))

        return result

    def build_structure(self):

        structure = self.dir_to_dict(self.root_img_path)
        print(json.dumps(structure, indent=2, ensure_ascii=False))

        return structure

    def f(self, image_path):

        # print(f'----------------{image_path}------------------{self.model}-------------------------------------')

        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read())

        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image;base64,{encoded_image_text}"
        # print(base64_qwen)

        a = time.time()
        chat_response = client.chat.completions.create(
            model=self.model,
            messages=[
                # {"role": "system", "content": "You are a helpful assistant."},
                {"role": "system", "content": "你是一个分类器."},
                {
                    "role": "user",
                    "content": [
                        { "type": "image_url", "image_url": { "url": base64_qwen } },
                        {"type": "text", "text": self.prompt}
                    ]
                }
            ],

            temperature = 0.01,
            top_p = 0.1
        )


        r = chat_response.choices[0].message.content
        # print("Chat response: ", r)

        b = time.time()

        # print(f'{image_path} {self.model} time: {b-a}, out len: {len(r)}, ratio: {len(r)/(b-a)}')

        return r

    def infer(self):

        ok = 0
        err = 0

        for type_, images in self.structure.items():

            for image in images:
                path_ = os.path.join(self.root_img_path, type_, image)
                r = self.f(path_)

                if r == type_:
                    ok += 1
                    print(f'ok: {ok}, predict: {r} == true: {type_}')

                else:
                    err += 1
                    print(f'err: {err}, predict: {r} != true: {type_}')

    def append_to_mllm(self):

        """
        {
            "messages": [
            {
                "content": "<image>请描述这张图片",
                "role": "user"
            },
            {
                "content": "中国宇航员桂海潮正在讲话。",
                "role": "assistant"
            },
            {
                "content": "他取得过哪些成就？",
                "role": "user"
            },
            {
                "content": "他于2022年6月被任命为神舟十六号任务的有效载荷专家，从而成为2023年5月30日进入太空的首位平民宇航员。他负责在轨操作空间科学实验有效载荷。",
                "role": "assistant"
            }
            ],
            "images": [
            "mllm_demo_data/3.jpg"
            ]
        }
        """

        with open(f'{self.cwd}/data/mllm_demo.json') as f:
            mllm = json.load(f)

        for type_, images in self.structure.items():
            for image in images:

                dict_ = {
                    "messages": [
                        {
                            "content": f"<image>{self.prompt}",
                            "role": "user"
                        },
                        {
                            "content": f"{type_}",
                            "role": "assistant"
                        }
                    ],
                    "images": [f'{self.img_dir}/{type_}/{image}']
                }

                mllm.append(dict_)

        with open(f'{self.cwd}/data/mllm_demo.json', 'w') as f:
            json.dump(mllm, f, ensure_ascii=False, indent=2)

        print(mllm)


xiolift = XioLift('tests/lsj/xiolift_img')
xiolift.infer()
# xiolift.append_to_mllm()

