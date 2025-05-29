import torch
from FlagEmbedding import FlagModel


class BGE:

    def __init__(self, conf):

        self.model = FlagModel(
            model_name_or_path=conf.model_path,
            query_instruction_for_retrieval=conf.query_instruction_for_retrieval,
            use_fp16=False)  # 49 环境下设为True会出问题

        self.dim = 1024

    def run(self):

        sentences_1 = ["样例数据-1", "样例数据-2"]
        sentences_2 = ["样例数据-3", "样例数据-4"]

        embeddings_1 = self.model.encode(sentences_1)
        embeddings_2 = self.model.encode(sentences_2)
        similarity = embeddings_1 @ embeddings_2.T

        print(similarity)

    def self_simi(self, neg: list):

        embeddings_2 = self.model.encode(neg)
        similarity = embeddings_2 @ embeddings_2.T

        return similarity

    def pred(self, q):

        v = self.model.encode(q)
        return torch.from_numpy(v).cpu()

