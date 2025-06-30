
from MyPrompt import*
import logging
import os
class Test:
    
    def test(self, type_2_images, full_img_path, local_qwen_api, retrieval):

        ok = 0
        err = 0
        unknown = 0

        classify_prompt = FILLING_CONTENT_PROMPT

        types = list(type_2_images.keys())

        for type_, images in type_2_images.items():

            # if type_ != '限速器钢丝绳张紧装置':
            #     continue

            for image in images:

                if 'aug' in image:
                    continue
                
                path_ = os.path.join(full_img_path, type_, image)

                logging.info(f'call {path_} with {classify_prompt}')

                p_type = local_qwen_api.local_inference(path_, system_prompt='你是一个分类器.', text_prompt=f'{classify_prompt}')

                if p_type in types:
                    scores = retrieval.scores(query=image, t_type=type_, p_type=p_type)

                    mean = scores.mean()
                    logging.info(f'got {p_type}, mean score: {mean}')
                    print(f'got {p_type}, mean score: {mean}')

                    if mean < 0.8:
                        p_type = '未知'
                else:
                    logging.info(f'got {p_type}, not in types')
                    print(f'got {p_type}, not in types')

                if p_type == '未知' or p_type not in types:
                    unknown += 1
                    s = f'unknown: {unknown}, predict: {p_type} and true: {type_} {image}'

                elif type_ == p_type:
                    ok += 1
                    s = f'ok: {ok}, predict: {p_type} == true: {type_} {image}'

                else:
                    err += 1
                    s = f'err: {err}, predict: {p_type} != true: {type_} {image}'

                print(s)
                logging.info(s)
