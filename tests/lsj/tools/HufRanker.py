import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class HufRanker:

    def __init__(self, conf):

        self.tokenizer = AutoTokenizer.from_pretrained('./bge-large-zh-v1.5-retriever')
        self.model = AutoModelForSequenceClassification.from_pretrained('./bge-large-zh-v1.5-retriever')
        self.model.eval()

    def pred(self, doc_qes):
        with torch.no_grad():
            inputs = self.tokenizer(doc_qes, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
            print(scores)

            return scores
