import numpy as np

class Sort:

    @staticmethod
    def descend(list_, key_):

        """
        list_ = [{'k': 3}, {'k': 1}]
        key = 'k'

        return [{'k': 3}, {'k': 1}]
        """
        return sorted(list_, key=lambda item: item[key_], reverse=True)

    @staticmethod
    def ascend(list_, key_):

        """
        list_ = [{'k': 3}, {'k': 1}]
        key = 'k'

        return [{'k': 1}, {'k': 3}]
        """
        return sorted(list_, key=lambda item: item[key_])

    @staticmethod
    def ascend2(list_, k1_, k2_):

        """
        list_ = [{'k1': 3, 'k2': 5}, {'k1': 1, 'k2': 3}]
        """
        return sorted(list_, key=lambda item: (item[k1_] + item[k2_]) / 2)

    @staticmethod
    def argsort(lst):

        # return 序号 array([0, 2, 1])

        a = np.argsort(np.array(lst))
        return list(reversed(a))

