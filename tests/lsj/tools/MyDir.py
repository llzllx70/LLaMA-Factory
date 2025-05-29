import os

from src.tools.MyPath import MyPath

class MyDir:

    def inner_get_files(self, ret, dir_, suffix=['.docx']):

        for root, dirs, files in os.walk(dir_):

            for file in files:

                _, name, ext = MyPath().split(file)

                if ext in suffix and name[0] != '.':
                    ret.append(f'{root}/{file}')

            for dir__ in dirs:
                self.get_files(f'{root}/{dir__}', suffix)

    def get_files(self, dir_, suffix=['.docx']):

        ret = []
        self.inner_get_files(ret, dir_, suffix)
        return ret

    @staticmethod
    def check_and_create(path):

        if not os.path.exists(path):
            os.makedirs(path)


