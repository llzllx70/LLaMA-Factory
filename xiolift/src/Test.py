
from MyPrompt import*
import logging
import os

UNKNOWN = '未知'
class Infer:

    def __init__(self, type_2_images, img_aug_dir, local_qwen_api, retrieval):

        self.type_2_images = type_2_images
        self.img_aug_dir = img_aug_dir
        self.local_qwen_api = local_qwen_api
        self.retrieval = retrieval

        self.classify_prompt = FILLING_CONTENT_PROMPT

    @property
    def types(self):
        return list(self.type_2_images.keys())

    def get_type(self, image):

        mean = 0
        p_type = self.local_qwen_api.local_inference(image, system_prompt='你是一个分类器.', text_prompt=f'{self.classify_prompt}')

        if p_type == '未知' or p_type not in self.types:
            p_type = UNKNOWN

        else:
            scores = self.retrieval.scores(query=image, p_type=p_type)
            mean = scores.mean()

            if mean < 0.85:
                p_type = UNKNOWN

        logging.info(f'predict {image} -> type: {p_type}, mean score: {mean}')
        return p_type

    def test(self):

        ok = 0
        err = 0
        unknown = 0

        for t_type, images in self.type_2_images.items():

            for image in images:

                if 'aug' in image:
                    continue
                
                image_path = os.path.join(self.img_aug_dir, t_type, image)

                p_type = self.get_type(image=image_path)

                if p_type == UNKNOWN:
                    unknown += 1
                    s = f'unknown: {unknown}, predict: {p_type} and true: {t_type} {image}'

                elif t_type == p_type:
                    ok += 1
                    s = f'ok: {ok}, predict: {p_type} == true: {t_type} {image}'

                else:
                    err += 1
                    s = f'err: {err}, predict: {p_type} != true: {t_type} {image}'

                print(s)
                logging.info(s)

