

import hashlib

class MyHash:

    @staticmethod
    def calculate_md5(input_string):
        md5_hash = hashlib.md5()
        md5_hash.update(input_string.encode('utf-8'))  # 转换为字节串进行计算
        return md5_hash.hexdigest()  # 返回十六进制表示的哈希值

    @staticmethod
    def calculate_file_md5(file_path):
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:  # 以二进制读模式打开文件
            for chunk in iter(lambda: f.read(4096), b""):  # 每次读取4096字节
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
