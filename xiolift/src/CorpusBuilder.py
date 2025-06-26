
import random
import json
import re
from MyPrompt import *
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

class CorpusGenerator:

    def __init__(self, cwd, img_dir, qwen_api=None):

        self.cwd = cwd
        
        self.image_builder = ImageCorpusBuilder(cwd, img_dir, qwen_api)
        self.text_builder = TextCorpusBuilder(cwd, img_dir, qwen_api)

    def build_sft(self, type_2_images, relation):

        self.image_builder.build_image_sft(type_2_images, relation)
        self.text_builder.build_text_sft(relation)

        sft = self.image_builder.sft + self.text_builder.sft

        random.shuffle(sft)

        with open(f'{self.cwd}/data/xiolift_generate_sft.json', 'w') as f:
            json.dump(sft, f, ensure_ascii=False, indent=2)

        print(sft)

class CorpusBuilder:

    def __init__(self, cwd, img_dir, qwen_api):
        self.cwd = cwd
        self.img_dir = img_dir

        self.sft = []
        self.sft_lock = Lock()

        self.qwen_api = qwen_api

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

class ImageCorpusBuilder(CorpusBuilder):

    def __init__(self, cwd, img_dir, qwen_api=None):
        super().__init__(cwd, img_dir=img_dir, qwen_api=qwen_api)   

    """生成式任务的语料库构建"""

    def build_image_sft(self, type_2_images, relation):

        self.build_one_image_sft(type_2_images)
        self.build_two_image_sft(type_2_images, relation)

    def append_image_corpus(self, messages, images):

        self.sft.append({
            "messages": messages,
            "images": images
        })

    def build_two_image_sft(self, type_2_images, relation):

        types = list(type_2_images.keys())

        for err in relation['error']:
            match = re.search(r'predict: (.*?) != true: (.*?) (s\d+_.*\.jpg)', err)
            if not match:
                continue
            
            p, t, image = match.groups()
            if p not in types:
                continue

            for e_image in type_2_images[p]:
                self.append_image_corpus(
                    self.build_two_filling_message(t, p),
                    [self.image_path(t, image), self.image_path(p, e_image)]
                )

    def build_one_image_sft(self, type_2_images):
        
        for type_, images in type_2_images.items():
            other_types = [t for t in type_2_images.keys() if t != type_]

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
        """生成选择任务的消息格式"""

        str_ = self.generate_choices(ok_type, other_types)
        return self.build_message(f"<image>请选择图片内容属于下面哪个类别: {str_}", ok_type)

    def build_filling_message(self, ok_type):
        """生成填空任务的消息格式"""
        return self.build_message("<image>请输出图片内容的正确类别", ok_type)

    def build_two_filling_message(self, ok, err):
        """生成填空任务的消息格式"""
        return self.build_message("<image><image>请按顺序输出两张图片内容的正确类别", f'{ok}, {err}')

    def build_judge_messages(self, ok_type, other_types):
        """生成判断任务的消息格式"""

        err_types = random.sample(other_types, 16)

        return [
            self.build_message(f"<image>请判断图片内容是否属于类别: {err_type}", "错误")
            for err_type in err_types
        ] + [
            self.build_message(f"<image>请判断图片内容是否属于类别: {ok_type}", "正确")
        ]


class TextCorpusBuilder(CorpusBuilder):

    def __init__(self, cwd, img_dir, qwen_api=None):
        super().__init__(cwd, img_dir=img_dir, qwen_api=qwen_api)

    """文本任务的语料库构建"""

    def build_text_sft(self, relation):

        self.from_system(relation['system'])
        self.from_relation(relation['relation'])
        self.from_desc(relation['desc'])

    def from_system(self, system):

        for ok_system, types in system.items():
            other_systems = [s for s in system.keys() if s != ok_system]
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
        
    def from_relation(self, relation):

        r = self.qwen_api.text_generate(text_prompt=QA_GENERATE_PROMPT.format(relation=relation))

        rr = json.loads(r)

        with self.sft_lock:
            for k, v in rr.items():
                self.sft.append({
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

    def from_desc(self, desc):

        def task(chunk):
            return self.from_relation(chunk)

        chunks = [desc[i:i+20] for i in range(0, len(desc), 20)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(task, chunk) for chunk in chunks]
            for future in as_completed(futures):
                # 捕捉异常
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in from_relation: {e}")

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
        """生成判断任务的消息格式"""

        err_system = random.sample(other_systems, 4)

        return [
            self.build_message(f"请判断{one_type}是否属于系统: {err_type}", "错误")
            for err_type in err_system
        ] + [
            self.build_message(f"请判断{one_type}是否属于系统: {ok_system}", "正确")
        ]
