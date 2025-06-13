
import pickle
import numpy as np
import os


class Serialize:

    @staticmethod
    def save_obj(obj_array, file_obj):

        # 一个doc的obj文件
        with open(file_obj, 'wb') as f:
            pickle.dump(obj_array, f)  # 用 dump 函数将 Python 对象转成二进制对象文件

    @staticmethod
    def save_vec(vec_array, file_npy):

        # 一个doc的npy文件
        np.save(file_npy, vec_array)

    @staticmethod
    def load_obj(file_obj):

        try:
            if not os.path.exists(file_obj):
                return None

            # 一个doc的obj文件
            with open(file_obj, 'rb') as f:
                return pickle.load(f)  # 将二进制文件对象转换成 Python 对象

        except Exception as e:
            return None

    @staticmethod
    def load_vec(file_npy):

        try:
            if not os.path.exists(file_npy):
                return None

            return np.load(file_npy)

        except Exception as e:
            return None
