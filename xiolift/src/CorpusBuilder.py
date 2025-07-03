
import random
import json
from tools.Json import Json
import re
import os
from MyPrompt import *
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from QwenApi import QwenApi
import logging

class CorpusGenerator:

    def build_sft(self, cwd, img_dir, type_2_images, infos):

        sft = [
            *Type2ImageBuilder(cwd, img_dir, type_2_images, infos).do_sft(),
            *SystemBuilder(cwd, img_dir, type_2_images, infos).do_sft(),
            # *ErrBuilder(cwd, img_dir, type_2_images, infos).do_sft(force=True),
            *RelationBuilder(cwd, img_dir, type_2_images, infos).do_sft(),
            *DescBuilder(cwd, img_dir, type_2_images, infos).do_sft()
        ]

        random.shuffle(sft)

        with open(f'{cwd}/data/xiolift_generate_sft.json', 'w') as f:
            json.dump(sft, f, ensure_ascii=False, indent=2)

    def build_desc_structure(self, cwd, img_dir, type_2_images, infos):

        desc_structure = DescStructureBuilder(cwd, img_dir, type_2_images, infos).build_desc_structure()

        with open(f'{cwd}/xiolift/infos/desc_structure.json', 'w') as f:
            json.dump(desc_structure, f, ensure_ascii=False, indent=2)

class CorpusBuilder:

    def __init__(self, cwd, img_dir, type_2_images=None, infos=None):

        self.cwd = cwd
        self.img_dir = img_dir
        self.type_2_images = type_2_images
        self.infos = infos

        self.sft = []
        self.sft_lock = Lock()

        self.qwen_api = QwenApi()

    @property
    def error(self):
        return self.infos.get('error', [])

    @property
    def relation(self):
        return self.infos.get('relation', {})

    @property
    def desc(self):
        return self.infos.get('desc', '')

    @property
    def system(self):
        return self.infos.get('system', {})

    @property
    def types(self):
        return list(self.type_2_images.keys()) if self.type_2_images else []

    @property
    def desc_structure_file(self):
        return f'{self.cwd}/xiolift/infos/desc_structure.json'

    @property
    def images(self):
        return [image for type_, images in self.type_2_images.items() for image in images]

    def do_sft(self, force=False):

        caller = type(self).__name__

        if force or not os.path.exists(f'{self.cwd}/data/{caller}_sft.json'):
            print(f"[Base] Calling build_sft from: {caller}")
            self.build_sft()
            Json.save(f'{self.cwd}/data/{caller}_sft.json', self.sft) 
            print(f'End of {caller}')

        else:
            print(f'Loading existing SFT from {caller}')
            self.sft = Json.load(f'{self.cwd}/data/{caller}_sft.json')

        return self.sft

    def image_path(self, type_, image):
        return f'{self.img_dir}/{type_}/{image}'

    def generate_choices(self, ok_choice, other_choices):

        k = random.randint(3, 5)
        choices = random.sample(other_choices, k) + [ok_choice]
        random.shuffle(choices)

        return str(choices)

    def build_message(self, user_content, ai_content):
        """生成消息格式"""
        return [
            {
                "content": user_content,
                "role": "user"
            },
            {
                "content": ai_content,
                "role": "assistant"
            }
        ]

    def append_image_corpus(self, messages, images):

        self.sft.append({
            "messages": messages,
            "images": images
        })

    def call_qwen_qa(self, chunk, save_to):

        r = self.qwen_api.text_generate(text_prompt=QA_GENERATE_PROMPT.format(info=chunk))

        rr = json.loads(r)

        with self.sft_lock:
            for k, v in rr.items():
                save_to.append({
                    "messages": [
                        {
                            "content": k,
                            "role": "user"
                        },
                        {
                            "content": v,
                            "role": "assistant"
                        }
                    ]
                })

    def call_image_desc(self, file, save_to):

        type_, image = file

        path_ = os.path.join(self.img_dir, type_, image)
        r = self.qwen_api.image_info(file=path_)

        logging.info(f"Image: {image}, Desc: {r}")

        with self.sft_lock:
            save_to[image] = r

    def batch_call_qwen(self, fn, chunks, save_to):

        with ThreadPoolExecutor(max_workers=100) as executor:
            # futures = [executor.submit(self.call_qwen_qa, chunk) for chunk in chunks]
            futures = [executor.submit(fn, chunk, save_to) for chunk in chunks]
            for future in as_completed(futures):
                # 捕捉异常
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in from_relation: {e}")

class Type2ImageBuilder(CorpusBuilder):

    """从type_2_images.json构建语料库"""

    def build_sft(self):
        
        for type_, images in self.type_2_images.items():
            other_types = [t for t in self.type_2_images.keys() if t != type_]

            for image in images:
                self.append_image_corpus(
                    self.build_choice_message(type_, other_types),
                    [self.image_path(type_, image)]
                )
                
                self.append_image_corpus(
                    self.build_filling_message(type_),
                    [self.image_path(type_, image)]
                )

                for message in self.build_judge_messages(type_, other_types):
                    self.append_image_corpus(
                        message,
                        [self.image_path(type_, image)]
                    )

    def build_choice_message(self, ok_type, other_types):
        str_ = self.generate_choices(ok_type, other_types)
        return self.build_message(f"<image>请选择图片内容属于下面哪个类别: {str_}", ok_type)

    def build_filling_message(self, ok_type):
        return self.build_message("<image>请输出图片内容的正确类别", ok_type)

    def build_judge_messages(self, ok_type, other_types):

        err_types = random.sample(other_types, 20)

        return [
            self.build_message(f"<image>请判断图片内容是否属于类别: {err_type}", "错误")
            for err_type in err_types
        ] + [
            self.build_message(f"<image>请判断图片内容是否属于类别: {ok_type}", "正确")
        ]

class SystemBuilder(CorpusBuilder):

    """from info.json['system']"""

    def build_sft(self):

        for ok_system, types in self.system.items():
            other_systems = [s for s in self.system.keys() if s != ok_system]
            for one_type in types:

                self.sft.append({
                        "messages": self.build_choice_message(one_type, ok_system, other_systems)
                    }
                )

                self.sft.append({
                        "messages": self.build_filling_message(one_type, ok_system)
                    }
                )

                for message in self.build_judge_messages(one_type, ok_system, other_systems):
                    self.sft.append({
                            "messages": message
                        }
                    )

    def build_choice_message(self, type_, ok_choice, other_choices):

        str_ = self.generate_choices(ok_choice, other_choices)

        return self.build_message(
            f"请选择{type_}属于下面哪个系统: {str_}",
            ok_choice
        )

    def build_filling_message(self, one_type, ok_choice):

        return self.build_message(
            f"请输出{one_type}属于哪个系统",
            ok_choice
        )
    
    def build_judge_messages(self, one_type, ok_system, other_systems):

        err_system = random.sample(other_systems, 4)

        return [
            self.build_message(f"请判断{one_type}是否属于系统: {err_type}", "错误")
            for err_type in err_system
        ] + [
            self.build_message(f"请判断{one_type}是否属于系统: {ok_system}", "正确")
        ]

class ErrBuilder(CorpusBuilder):
    
    def build_sft(self):

        for err in self.error:
            match = re.search(r'predict: (.*?) != true: (.*?) (s\d+_.*\.jpg)', err)
            if not match:
                continue
            
            p_type, t_type, image = match.groups()

            self.append_image_corpus(
                self.build_message(f"<image>请判断图片内容是否属于类别: {p_type}", "错误"),
                [self.image_path(t_type, image)]
            )

            if p_type not in self.types:
                self.sft.append({
                        "messages": self.build_message(f"电梯系统中是否存在一种部件名为{p_type}", f"当前系统不存在部件{p_type}"),
                    }
                )
            else:
                for e_image in self.type_2_images[p_type]:
                    self.append_image_corpus(
                        self.build_two_filling_message(t_type, p_type),
                        [self.image_path(t_type, image), self.image_path(p_type, e_image)]
                    )

    def build_two_filling_message(self, ok, err):
        return self.build_message("<image><image>请按顺序输出两张图片内容的正确类别", f'{ok}, {err}')

class RelationBuilder(CorpusBuilder):
    
    """from info.json['relation']"""

    def build_sft(self):
        self.call_qwen_qa(self.relation)

class DescBuilder(CorpusBuilder):

    """from info.json['desc']"""

    def build_sft(self):

        chunks = [self.desc[i:i+20] for i in range(0, len(self.desc), 20)]

        self.batch_call_qwen(fn=self.call_qwen_qa, chunks=chunks, save_to=self.sft)


class DescStructureBuilder(CorpusBuilder):
    
    """构建desc_structure.json"""

    def build_desc_structure(self):

        if os.path.exists(self.desc_structure_file):
            return Json.load(self.desc_structure_file)

        else:
            desc_ = {}

            chunks = []

            for type_, images in self.type_2_images.items():
                for image in images:
                    chunks.append((type_, image))
                
            self.batch_call_qwen(fn=self.call_image_desc, chunks=chunks, save_to=desc_)
            return desc_
