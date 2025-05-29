
class MyStr:

    @staticmethod
    def to_plain(str_):
        # 去掉转义字符
        return ''.join(str_.split())

