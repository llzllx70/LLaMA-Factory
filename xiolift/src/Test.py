
from MyPrompt import*
import logging
import os

class Test:
    
    def test(self, id_to_key, key_to_id, structure, full_img_path, local_qwen_api):

        ok = 0
        err = 0

        classify_prompt = SFT_USER_PROMPT.format(id_2_key=id_to_key)

        for type_, images in structure.items():

            # if type_ != '限速器钢丝绳张紧装置':
            #     continue

            for image in images:

                if 'aug' in image:
                    continue
                
                path_ = os.path.join(full_img_path, type_, image)

                logging.info(f'call {path_} with {classify_prompt}')

                r = local_qwen_api.local_inference(path_, system_prompt='你是一个分类器.', text_prompt=f'{classify_prompt}')

                logging.info(f'got {r}')

                p_id = self.extract_classify(r)
                p_type = id_to_key[p_id]

                t_id = key_to_id[type_]

                if p_id == t_id:
                    ok += 1
                    s = f'ok: {ok}, predict: {p_id}:{p_type} == true: {t_id}:{type_} {image}'
                    print(s)
                    logging.info(s)

                else:
                    err += 1
                    s = f'err: {err}, predict: {p_id}:{p_type} != true: {t_id}:{type_} {image}'
                    print(s)
                    logging.info(s)
