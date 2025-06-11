
import re
import os
import json
import time
import base64
from openai import OpenAI
import argparse

import shutil
from tools.Json import Json

from QwenApi import QwenApi
from ImageAugment import ImageAugment

# Set OpenAI's API key and API base to use vLLM's API server.

parser = argparse.ArgumentParser(description="示例：添加命令行参数")
parser.add_argument("--task", type=str, required=False, help="test")
args = parser.parse_args()

openai_api_key = "EMPTY"
openai_api_base = "http://172.16.2.49:8002/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

CLASSIFY_PROMPT = """<image>图片是电梯某个部件的照片，有如下类别及对应的描述信息:
【{info}】
请依据图片信息及各类别的描述信息，区别当前图片属于哪个类别，先对图片进行描述，再输出类别。 格式如下:
描述:【xxx】,
此描述信息最匹配的类别:【yyy】
"""

ANSWER_PROMPT = """描述:【{desc}】,
此描述信息最匹配的类别:【{type}】
"""

DESCRIBE_PROMPT = """请对图片的关键特性进行描述，描述内容包括此部件的特性、用途、特点等信息，不需要具体指出部件的名称，忽视颜色等无关信息。"""


class XioLift:

    def __init__(self, img_dir, info_dir):

        self.cwd = os.getcwd()

        self.model = "Qwen2.5-VL-7B-Instruct"

        self.img_dir = img_dir
        self.info_dir = info_dir
        
        self.full_img_path = f'{self.cwd}/{img_dir}'
        self.full_info_path = f'{self.cwd}/{info_dir}'

        self.info_file = f'{self.full_info_path}/info.json'
        self.structure_file = f'{self.full_info_path}/structure.json'
        self.desc_structure_file = f'{self.full_info_path}/desc_structure.json'

        self.structure = self.build_structure()
        self.types = list(self.structure.keys())

        self.info = Json.load(self.info_file)

        self.qwen_api = QwenApi()

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

        if os.path.exists(self.structure_file):
            return Json.load(self.structure_file)

        else:
            structure = self.dir_to_dict(self.full_img_path)
            Json.save(self.structure_file, structure)

        print(json.dumps(structure, indent=2, ensure_ascii=False))
        return structure

    def build_desc_structure(self):

        if os.path.exists(self.desc_structure_file):
            return Json.load(self.desc_structure_file)

        structure = self.build_structure()

        desc_structure = {}

        for type_, images in structure.items():

            l = []
            for image in images:
                path_ = os.path.join(self.full_img_path, type_, image)

                l.append(
                    {
                        'name': image,
                        'desc': self.call(path_, system_prompt='你是一个图片内容提取器', text_prompt=DESCRIBE_PROMPT)
                    }
                )

            desc_structure[type_] = l

        print(json.dumps(structure, indent=2, ensure_ascii=False))

        Json.save(self.desc_structure_file, desc_structure)

        return desc_structure

    def call(self, image_path, system_prompt, text_prompt, base64_qwen=None):

        # print(f'----------------{image_path}------------------{self.model}-------------------------------------')

        if base64_qwen is None:
            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read())

            encoded_image_text = encoded_image.decode("utf-8")
            base64_qwen = f"data:image;base64,{encoded_image_text}"

        chat_response = client.chat.completions.create(
            model=self.model,
            messages=[
                # {"role": "system", "content": "You are a helpful assistant."},
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        { "type": "image_url", "image_url": { "url": base64_qwen } },
                        {"type": "text", "text": text_prompt}
                    ]
                }
            ],

            temperature = 0.01,
            top_p = 0.1
        )

        r = chat_response.choices[0].message.content
        # print("Chat response: ", r)

        return r

    def extract_classify(self, content):

        match = re.search(r"类别[：:]\s*【(.+?)】", content)
        if match:
            return match.group(1)

        else:
            return content

    def test(self):

        ok = 0
        err = 0

        classify_prompt = CLASSIFY_PROMPT.format(info=self.info)

        for type_, images in self.structure.items():

            for image in images:
                path_ = os.path.join(self.full_img_path, type_, image)
                r = self.call(path_, system_prompt='你是一个分类器.', text_prompt=f'{classify_prompt}')
                r = self.extract_classify(r)

                if r == type_:
                    ok += 1
                    print(f'ok: {ok}, predict: {r} == true: {type_}')

                else:
                    err += 1
                    print(f'err: {err}, predict: {r} != true: {type_}')

    def parse(self):

        for type_, images in self.structure.items():

            describe_prompt = DESCRIBE_PROMPT.format(type=type_)

            for image in images:

                path_ = os.path.join(self.full_img_path, type_, image)
                r = self.call(path_, system_prompt='你是一个图片内容提取器', text_prompt=describe_prompt)

    def build_xiolift_sft(self):

        """
        {
            "messages": [
            {
                "content": "他取得过哪些成就？",
                "role": "user"
            },
            {
                "content": "他于2022年6月被任命为神舟十六号任务的有效载荷专家，从而成为2023年5月30日进入太空的首位平民宇航员。他负责在轨操作空间科学实验有效载荷。",
                "role": "assistant"
            }
            ],
            "images": [ "mllm_demo_data/3.jpg"]
        }
        """

        sft = []
        desc_structure = self.build_desc_structure()

        for type_, images in desc_structure.items():
            for image in images:

                dict_ = {
                    "messages": [
                        {
                            "content": f"{CLASSIFY_PROMPT.format(info=self.info)}",
                            "role": "user"
                        },
                        {
                            "content": f"{ANSWER_PROMPT.format(desc=image['desc'], type=type_)}",
                            "role": "assistant"
                        }
                    ],
                    "images": [f'{self.img_dir}/{type_}/{image["name"]}']
                }

                sft.append(dict_)

        with open(f'{self.cwd}/data/xiolift_sft.json', 'w') as f:
            json.dump(sft, f, ensure_ascii=False, indent=2)

        print(sft)

    def build_xiolift_dpo(self):

        """
        {
            'conversations': [
                {'from': 'human', 'value': '<image>What are the key features you observe in the image?'}
            ], 
            'chosen': {'from': 'gpt', 'value': 'A young man standing on stage wearing a white shirt and black pants.'}, 
            'rejected': {'from': 'gpt', 'value': 'A young man standing on stage wearing white pants and shoes.'}, 
            'images': [<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=336x470 at 0x7296B48DD820>]
        }
        """
        jsonl_ =[]
        import random

        desc_structure = self.build_desc_structure()

        for this_type_, images in desc_structure.items():
            for image in images:
                for type_ in self.types: 
                    if type_ == this_type_:
                        continue

                    r_image = random.choice(desc_structure[type_])

                    dict_ = {
                        "conversations": [{"from": "human", "value": f"<image>{CLASSIFY_PROMPT.format(types=str(self.types))}"}],
                        'chosen': {'from': 'gpt', 'value': f'{ANSWER_PROMPT.format(desc=image["desc"], type=this_type_)}'}, 
                        'rejected': {'from': 'gpt', 'value': f'{ANSWER_PROMPT.format(desc=r_image["desc"], type=type_)}'}, 
                        "images": [f'{self.img_dir}/{this_type_}/{image["name"]}']
                    }

                    jsonl_.append(dict_)

        with open(f'{self.cwd}/data/dpo_xiolift.jsonl', 'w') as f:
            for l in jsonl_:
                f.write(json.dumps(l, ensure_ascii=False) + '\n')

    def format_new_corpus(self):
        

        # 设置你的根目录路径
        root_dir = f'{self.cwd}/tests/lsj/部件识别'  # 修改为你的实际路径
        output_dir = f'{self.cwd}/tests/lsj/xiolift_img'   # 分类保存的输出路径

        # 正则匹配去掉 (2) 之类的序号，提取类别名
        def extract_category(filename):
            return re.sub(r'\s*\(\d+\)', '', filename)

        # 遍历根目录
        for folder_name in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue  # 忽略非目录

            for file in os.listdir(folder_path):
                if not file.lower().endswith('.jpg'):
                    continue
                category = extract_category(os.path.splitext(file)[0])
                category_dir = os.path.join(output_dir, category)

                os.makedirs(category_dir, exist_ok=True)

                src_file = os.path.join(folder_path, file)
                dst_filename = f"{folder_name}_{file}"
                dst_file = os.path.join(category_dir, dst_filename)

                shutil.copy2(src_file, dst_file)  # 或 shutil.move(src_file, dst_file) 进行移动
                print(f"复制: {src_file} -> {dst_file}")

    def extract_classify_info(self):

        for classify, files in self.structure.items():

            files = [os.path.join(self.full_img_path, classify, file) for file in files]

            desc = self.qwen_api.classify_info(classify, files)

            self.info[classify] = desc
            
        Json.save(self.info_file, self.info)

    def augment(self):

        """
        图像增强
        """

        input_dir = f'{self.cwd}/tests/lsj/xiolift_img'
        output_dir = f'{self.cwd}/tests/lsj/xiolift_img_aug'

        target_num_per_class = 6
        
        aug = ImageAugment(input_dir, output_dir, target_num_per_class)
        aug.augment()


if __name__ == '__main__':

    xiolift = XioLift('tests/lsj/xiolift_img_aug', 'tests/lsj/infos')

    if args.task == 'test':
        xiolift.test()

    if args.task == 'format_new_corpus':
        # xiolift.format_new_corpus()
        pass

    if args.task == 'extract_classify_info':
        xiolift.extract_classify_info()

    if args.task == 'build_xiolift_sft':
        xiolift.build_xiolift_sft()

    if args.task == 'build_xiolift_dpo':
        xiolift.build_xiolift_dpo()

    if args.task == 'build_desc_structure':
        xiolift.build_desc_structure()

    if args.task == 'parse':
        xiolift.parse()

    if args.task == 'augment':
        xiolift.augment()
