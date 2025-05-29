

import re

class MyRE:

    @staticmethod
    def match(reg, str_):
        a = re.match(reg, str_)
        return a

    @staticmethod
    def matched(reg, str_):
        r = re.findall(reg, str_)
        return True if len(r) > 0 else False

    @staticmethod
    def sub(reg, to, str_):
        # str_ 中满足 reg 的，替换为to
        return re.sub(reg, to, str_)

    @staticmethod
    def finditer(reg, str_):

        # multiline
        return re.finditer(reg, str_, re.M)

    @staticmethod
    def split(flag, str_):
        return re.split(flag, str_)

    @staticmethod
    def contains_keyword(reg, sentence):
        # keywords = r'以上|以下|不超过|不得超过|超过|不低于|不得低于|低于|不得高于|不高于|高于|工作日内|天内|日内'
        pattern = re.compile(reg)
        if re.search(pattern, sentence):
            return True
        else:
            return False

    @staticmethod
    def contains_alphanumeric(sentence):

        pattern = re.compile(r'[0-9]')
        if re.search(pattern, sentence):
            return True
        else:
            return False

    @staticmethod
    def num_and_unit(sentence):
        # 数值 + 单位
        pattern = re.compile(r"[0123456789两零一二三四五六七八九十百千万亿]+(?:千|万|元|个|日|天|倍|人|位|只|岁|周|年|分|秒|名|公里|米|厘米|毫米|分米|次)")
        if re.search(pattern, sentence):
            return True
        else:
            return False

    @staticmethod
    def chinesenum_and_unit(sentence):
        # 数值 + 单位
        pattern = re.compile(r"[两零一二三四五六七八九十百千万亿]+(?:千|万|元|个|日|天|倍|人|位|只|岁|周|年|分|秒|名|公里|米|厘米|毫米|分米|次)")
        if re.search(pattern, sentence):
            return True
        else:
            return False

    @staticmethod
    def match_num(sentence):

        return MyRE.contains_alphanumeric(sentence) or MyRE.num_and_unit(sentence)

    def is_title(self, str_):

        # 注意中英文空格
        b = r'^[ \t　]*'
        e = r'.*$'
        n = r'0123456789零一二三四五六七八九十'

        reg = fr'{b}(([{n}]+[.、]+)|(第[{n}]+[章节条])){e}'

        return self.matched(reg, str_)

