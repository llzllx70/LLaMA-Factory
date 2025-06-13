import numpy as np
import torch
import torch.nn.functional as F
from src.tools.MyList import MyList

class MyNumpy:

    def __init__(self, array=None):
        self.array = array  # 是numpy

    def to_tensor(self):
        return torch.from_numpy(self.array)

    def concate_vec(self, a):

        """
        a 是numpy
        注：此函数已废弃，因为涉及多次内存分配， 使用OptimizedArrayWithDeque, 可提升30m -> 20s
        """

        a = a.reshape(-1, len(a))
        self.concate_matrix(a)

    def concate_matrix(self, a):

        """
        注：此函数已废弃，因为涉及多次内存分配， 使用OptimizedArrayWithDeque, 可提升30m -> 20s

        a: matrix ndarray
        注意此处的输入a是矩阵, 如果是向量，则不行
        a1: ndarray: [[1, 2]]
        a2: ndarray: [[3, 4]]

        return [
            [1, 2],
            [3, 4]
        ]
        """

        if self.array is None:
            self.array = a

        else:
            # self.array = np.concatenate([self.array, a])
            self.array = np.vstack([self.array, a])

    def delete(self, beg, end):

        # 不包括end
        self.array = np.delete(self.array, np.s_[beg:end], axis=0)

    def to_ndarray(self):
        return self.array

    @staticmethod
    def ascend_sort(ndarray):
        return np.argsort(ndarray)

    @staticmethod
    def descend_sort(ndarray):
        a = np.argsort(ndarray)
        return list(reversed(a))

    @staticmethod
    def sort_by_index(list1, list2, topk=5):

        """
        list2 作为score，对list1进行排序，输出topk
        """

        topk_idx = MyNumpy.topk_index(list2, topk)

        return [list1[idx] for idx in topk_idx]

    @staticmethod
    def topk_index(ndarray, topk=5):

        """
        取ndarray中最大的topk项，返回index和value
        从大到小排列
        """

        if type(ndarray) is list:
            ndarray = np.array(ndarray)

        index_ = MyNumpy.descend_sort(ndarray)[0:topk]

        return index_

    def to_tensor(self):
        return torch.from_numpy(self.array)

    @staticmethod
    def top_k_1(vec, matrix, nodes, topk=5, duplicate=False):

        if type(matrix) is MyNumpy:
            score = F.cosine_similarity(matrix.to_tensor(), vec).numpy()

        else:
            score = F.cosine_similarity(torch.from_numpy(matrix), vec).numpy()

        topk_idx = MyNumpy.topk_index(score, topk)

        score_ = list(score[topk_idx])

        topk_node, idx = MyList.filter(nodes, topk_idx, duplicate=duplicate)

        return topk_node, idx, score_

    @staticmethod
    def batch_cosine_similarity(x, y, batch_size=10000):

        # 计算余弦相似度时，按批次分割数据，避免一次加载整个数据集
        similarities = []
        num_batches = (x.size(0) + batch_size - 1) // batch_size  # 计算批次数
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, x.size(0))

            batch_x = x[start_idx:end_idx]

            batch_sim = F.cosine_similarity(batch_x, y)
            similarities.append(batch_sim)

        return torch.cat(similarities)

    @staticmethod
    def top_k(vec_wrap, qes, matrix, nodes, topk=5, duplicate=False):

        vec = vec_wrap.run(qes)

        if type(matrix) is MyNumpy:
            # score = F.cosine_similarity(matrix.to_tensor(), vec).numpy()
            score = MyNumpy.batch_cosine_similarity(matrix.to_tensor(), vec).numpy()

        else:
            # score = F.cosine_similarity(torch.from_numpy(matrix), vec).numpy()
            score = MyNumpy.batch_cosine_similarity(torch.from_numpy(matrix), vec).numpy()

        topk_idx = MyNumpy.topk_index(score, topk)

        score_ = list(score[topk_idx])

        topk_node, idx = MyList.filter(nodes, topk_idx, duplicate=duplicate)

        return topk_node, idx, score_

    @staticmethod
    def top_k_idx_score(vec, matrix, topk=5):

        if type(matrix) is MyNumpy:
            score = F.cosine_similarity(matrix.to_tensor(), torch.from_numpy(vec)).numpy()

        else:
            score = F.cosine_similarity(torch.from_numpy(matrix), vec).numpy()

        topk_idx = MyNumpy.topk_index(score, topk)

        score_ = list(score[topk_idx])

        return topk_idx, score_

    def softmax(x):

        # softmax([1, 2, 3]) -> [0.1, 0. 4, 0.5]
        exp_x = np.exp(x)
        a = exp_x / np.sum(exp_x)
        return a.tolist()


from collections import deque

class OptimizedArrayWithDeque:

    def __init__(self):
        self.array = deque()  # 使用deque保存数据

    def add_1d_array(self, a):
        a = a.reshape(-1, len(a))
        self.array.extend(a)

    def add_2d_array(self, a):
        # 将二维数据行添加到deque中
        self.array.extend(a)

    def get_array(self):
        # 将deque转换为numpy数组
        return np.array(list(self.array))


if __name__ == '__main__':

    # 示例用法
    optimized_array = OptimizedArrayWithDeque()

    a = np.array([[1, 2], [3, 4], [5, 6]])
    optimized_array.add_2d_array(a)

    a = np.array([[2, 2], [3, 4], [5, 6]])
    optimized_array.add_2d_array(a)

    a = np.array([[3, 2], [3, 4], [5, 6]])
    optimized_array.add_2d_array(a)

    # 获取最终的numpy数组
    final_array = optimized_array.get_array()
    print(final_array)


    a = np.empty((0, 2))
    print(a)

