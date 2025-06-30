
from MyPrompt import*
import logging
import os

class Test:
    
    def test(self, id_to_key, key_to_id, structure, full_img_path, local_qwen_api):

        ok = 0
        err = 0
        unknown = 0

        classify_prompt = FILLING_CONTENT_PROMPT

        for type_, images in structure.items():

            # if type_ != '限速器钢丝绳张紧装置':
            #     continue

            for image in images:

                if 'aug' in image:
                    continue
                
                path_ = os.path.join(full_img_path, type_, image)

                logging.info(f'call {path_} with {classify_prompt}')

                p_type = local_qwen_api.local_inference(path_, system_prompt='你是一个分类器.', text_prompt=f'{classify_prompt}')

                logging.info(f'got {p_type}')

                if p_type == '未知':
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
