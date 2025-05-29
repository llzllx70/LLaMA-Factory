
import argparse

class MyArgParser:

    def __init__(self):

        self.parser = argparse.ArgumentParser()

    def add_int_arg(self, arg, default=''):
        self.parser.add_argument(f"--{arg}", default=default, type=int)

    def add_str_arg(self, arg, default=''):
        self.parser.add_argument(f"--{arg}", default=default, type=str)

    def add_list_arg(self, arg, default=''):
        self.parser.add_argument(f'--{arg}', nargs='+', type=int, help='A list of integers')

    def get_args(self):
        return self.parser.parse_args()

    def check_args(self, arg, value):

        if self.parser.__getattribute__(arg) == value:
            return True

        return False

