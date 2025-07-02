import os
import torch
from transformers import AutoModel

import logging

MODEL_NAME = "models/bge-vl-large" 

class Retrierer:

    def __init__(self):
    
        self.model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True) # You must set trust_remote_code=True
        self.model.set_processor(MODEL_NAME)
        self.model.eval()
        self.cwd = 'xiolift/xiolift_img_aug'

    def files(self, type_):
        directory = f'{self.cwd}/{type_}'
        return [f'{directory}/{f}' for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    def scores(self, query, p_type):

        logging.info(f'retrieval get request: query: {query}, p_type: {p_type}')

        # query = f'{self.cwd}/{query}'
        candidates = self.files(p_type)

        with torch.no_grad():

            query = self.model.encode(images=query)
            candidates = self.model.encode(images=candidates)
            
            scores = query @ candidates.T

        # print(scores) 

        return scores


if __name__ == "__main__":

    r = Retrierer()

    l = [
        "单向弹性滑动导靴;弹性滚动导靴;s06_弹性滚动导靴 (2).jpg",
        "层门上坎应急导向装置;层门上坎;补_层门上坎.jpg",
        "导轨支架;导轨连接板;s03_T型导轨连接板 (2).jpg",
        "固定式滚动导靴;门锁滚轮;s07_门锁滚轮3.jpg",
        "限速器棘爪;限速器棘轮;补_限速器棘轮.jpg",
        "层门紧急开锁装置;固定式滑动导靴;s03_固定式滑动导靴2.jpg",
        "层门门锁机械锁钩;钳盘式制动器;补_钳盘式制动器 (2).jpg",
        "限速器棘爪;防托槽机构;s06_防托槽机构.jpg",
        "曳引机;全盘式制动器;补_全盘式制动器 (3).jpg",
        "曳引机;全盘式制动器;补_全盘式制动器.jpg",
        "单向弹性滑动导靴;对重块加托;s07_对重块加托.jpg",
        "层门门锁机械锁钩;限速器开关;补_限速器开关 (2).jpg",
        "导轨连接板;导轨支架;s06_导轨支架.jpg",
        "油杯;曳引轮防脱槽机构;s03_曳引轮防脱槽机构.jpg",
        "导轨支架;导轨压板;s03_导轨压板.jpg",
        "导轨支架;导轨压板;s06_导轨压板.jpg",
        "层门上坎;轿厢门楣;s03_轿厢门楣.jpg"
    ]

    for l_ in l:

        a, b, c = l_.split(';')

        r.scores(query=f'{c}/{b}', p_type=a)
