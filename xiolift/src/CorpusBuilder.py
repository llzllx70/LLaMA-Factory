
import random
import json
from MyPrompt import *

class CorpusBuilder:

    def build_sft(self, desc_structure):

        sft = []

        for type_, images in desc_structure.items():

            conslusion = self.info[type_]

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