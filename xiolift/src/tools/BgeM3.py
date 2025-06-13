import torch
from FlagEmbedding import BGEM3FlagModel


class BGEM3:

    def __init__(self, kwargs):

        self.model = BGEM3FlagModel(**kwargs)  # 49 环境下设为True会出问题

    def run(self, q, return_info):

        v = self.model.encode(q, **return_info)['dense_vecs']

        if return_info['return_dense']:
            d = v['dense_vecs']

        if return_info['return_sparse']:
            s = v['lexical_weights']

        return torch.from_numpy(v).cpu()

    def dense(self, q):

        v = self.model.encode(q)['dense_vecs']

        return torch.from_numpy(v).cpu()

    def sparse(self, q):

        v = self.model.encode(q, return_dense=False, return_sparse=True)['lexical_weights']

        return v

    def lexical_score(self, q1, q2):

        if type(q1) is str:
            a = self.sparse(q1)
        else:
            a = q1

        b = self.sparse(q2)

        return self.model.compute_lexical_matching_score(a, b)

    def dense_and_sparse(self, q):

        v = self.model.encode(q, return_dense=True, return_sparse=True)
        d = v['dense_vecs']
        s = v['lexical_weights']

        return torch.from_numpy(d).cpu(), s

