import torch
from torch import *
from src.wrap.VecWrap import VecWrap
from src.tools.MyNumpy import MyNumpy
from torch.utils.tensorboard import SummaryWriter


class Tensorboard:

    def __init__(self, vec_wrap: VecWrap, conf):

        self.conf = conf
        self.vec_wrap = vec_wrap

        self.writer = SummaryWriter('runs/embeddings')

    def projector(self, fs, ss):

        """
        fs: 泛化语义列表
        ss: 标准语义列表
        """

        features = MyNumpy()

        label = []

        s_ss = list(set(ss))

        for f, s in zip(fs, ss):
            v = self.vec_wrap.run(f)
            features.concate_vec(v)
            label.append(f'{s}:{f}')

        for s in s_ss:
            v = self.vec_wrap.run(s)
            features.concate_vec(v)
            label.append(f'{s}:@@')

        features = features.to_tensor()

        self.writer.add_embedding(
            mat=features,
            metadata=label  # label
        )

        print(t)


