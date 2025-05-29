
import random

class MyRandom:

    def __init__(self):
        self.random = random.Random()

    def int(self, b, e):
        return self.random.randint(b, e)

    @staticmethod
    def shuffle(list_):
        random.shuffle(list_)

    def random_item(self, list_):

        idx = self.int(0, len(list_) - 1)
        return list_[idx]

    def colon(self):

        a = [':', ': ', ' :', ' : ']
        b = ['；', '； ', ' ；', ' ； ']

        return self.random_item(a+b)

    def comma(self):

        a = [',', ', ', ' ,', ' , ']
        b = ['，', '， ', ' ，', ' ， ']

        return self.random_item(a+b)

    def stop(self):

        a = ['.', '. ', ' .', ' . ']
        b = ['。', '。 ', ' 。', ' 。 ']

        return self.random_item(a+b)



