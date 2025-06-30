import os
import torch
from transformers import AutoModel

MODEL_NAME = "models/bge-vl-large" 

class Retrierer:

    def __init__(self):
    
        self.model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True) # You must set trust_remote_code=True
        self.model.set_processor(MODEL_NAME)
        self.model.eval()

    def scores(self, query, candidates):

        with torch.no_grad():

            query = self.model.encode(images=query)
            candidates = self.model.encode(images=candidates)
            
            scores = query @ candidates.T

        print(scores) 

r = Retrierer()

a = 'xiolift/xiolift_img_aug/'

def files(type_):

    directory = f'{a}{type_}'

    return [f'{directory}/{f}' for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

r.scores(
    # query=f'{a}/轿厢护脚板/补_轿厢护脚板 (2).jpg',
    # candidates=files('层门被动门扇')
    # candidates=files('轿厢护脚板')

    # query=f'{a}/T型导轨连接板/s03_T型导轨连接板 (2).jpg',
    # candidates=files('导轨支架')
    # candidates=files('T型导轨连接板架')
    # candidates=files('轿厢护脚板')
    # candidates=files('中分门')

    query = f'{a}/弹性滚动导靴/s06_弹性滚动导靴 (2).jpg',
    candidates=files('单向弹性滑动导靴')
)
