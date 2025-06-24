
import random
import json
from MyPrompt import *

class CorpusBuilder:

    def __init__(self, cwd, img_dir):
        self.cwd = cwd
        self.img_dir = img_dir

    def image_path(self, type_, image):
        """获取图片的完整路径"""
        return f'{self.img_dir}/{type_}/{image}'

    def build_sft(self, desc_structure):

        sft = []

        for type_, images in desc_structure.items():

            for image in images:

                dict_ = {
                    "messages": [
                        {
                            "content": f"{SFT_USER_PROMPT.format(id_2_key=self.id_to_key)}",
                            "role": "user"
                        },
                        {
                            # "content": f"{SFT_ASSISTANT_PROMPT.format(desc=image['desc'], conclusion=conslusion, type=type_)}",
                            "content": f"{SFT_ASSISTANT_PROMPT.format(index=self.key_to_id[type_])}",
                            "role": "assistant"
                        }
                    ],
                    "images": [f'{self.img_dir}/{type_}/{image["name"]}']
                }

                sft.append(dict_)

        random.shuffle(sft)

        with open(f'{self.cwd}/data/xiolift_sft.json', 'w') as f:
            json.dump(sft, f, ensure_ascii=False, indent=2)

        print(sft)

    def build_dpo(self, desc_structure):

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

        jsonl_ = []

        for this_type_, images in desc_structure.items():
            for image in images:
                for type_ in self.types: 
                    if type_ == this_type_:
                        continue

                    r_image = random.choice(desc_structure[type_])

                    dict_ = {
                        "conversations": [{"from": "human", "value": f"{DPO_CLASSIFY_PROMPT.format(info=self.info)}"}],
                        'chosen': {'from': 'gpt', 'value': f'{DPO_ANSWER_PROMPT.format(desc=image["desc"], type=this_type_)}'}, 
                        'rejected': {'from': 'gpt', 'value': f'{DPO_ANSWER_PROMPT.format(desc=r_image["desc"], type=type_)}'}, 
                        "images": [f'{self.img_dir}/{this_type_}/{image["name"]}']
                    }

                    jsonl_.append(dict_)

        with open(f'{self.cwd}/data/dpo_xiolift.jsonl', 'w') as f:
            for l in jsonl_:
                f.write(json.dumps(l, ensure_ascii=False) + '\n')


class GenerateCorpusBuilder(CorpusBuilder):

    def __init__(self, cwd, img_dir):
        super().__init__(cwd, img_dir=img_dir)   

    """生成式任务的语料库构建"""

    def build_sft(self, type_2_images):
        
        sft = []

        for type_, images in type_2_images.items():

            other_types = [t for t in type_2_images.keys() if t != type_]

            for image in images:
                sft.append(
                    {
                        "messages": self.build_choice_message(type_, other_types),
                        "images": self.image_path(type_, image)
                    }
                )
                
                sft.append(
                    {
                        "messages": self.build_filling_message(type_),
                        "images": self.image_path(type_, image)
                    }
                )

                for message in self.build_judge_messages(type_, other_types):
                    sft.append(
                        {
                            "messages": message,
                            "images": self.image_path(type_, image)
                        }
                    )

        random.shuffle(sft)

        with open(f'{self.cwd}/data/xiolift_generate_sft.json', 'w') as f:
            json.dump(sft, f, ensure_ascii=False, indent=2)
           
    def build_choice_message(self, ok_type, other_types):
        """生成选择任务的消息格式"""

        k = random.randint(3, 5)
        chosen_types = random.sample(other_types, k) + [ok_type]
        random.shuffle(chosen_types)

        return [
            {
                "content": f"<image>请选择图片内容属于下面哪个类别: {', '.join(chosen_types)}",
                "role": "user"
            },
            {
                "content": ok_type,
                "role": "assistant"
            }
        ]

    def build_filling_message(self, ok_type):
        """生成填空任务的消息格式"""

        return [
            {
                "content": f"<image>请输出图片内容的正确类别",
                "role": "user"
            },
            {
                "content": f"{ok_type}",
                "role": "assistant"
            }
        ]

    def build_judge_messages(self, ok_type, other_types):
        """生成判断任务的消息格式"""

        err_types = random.sample(other_types, 16)

        return [
            [
                {
                    "content": f"<image>请判断图片内容是否属于类别: {err_type}",
                    "role": "user"
                },
                {
                    "content": "错误",
                    "role": "assistant"
                }
            ] for err_type in err_types
        ] + [
            [
                {
                    "content": f"<image>判断图片内容是否属于类别: {ok_type}",
                    "role": "user"
                },
                {
                    "content": "正确",
                    "role": "assistant"
                }
            ] 
        ]


