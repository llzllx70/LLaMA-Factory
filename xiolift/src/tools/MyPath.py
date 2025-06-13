
import os

class MyPath:

    @staticmethod
    def split(file_):

        # 分割路径名、文件名和后缀
        path_, name_ = os.path.split(file_)
        name_, ext_ = os.path.splitext(name_)

        return path_, name_, ext_

    def path(self, file_):
        return self.split(file_)[0]

    def name(self, file_):
        return self.split(file_)[1]

    def ext(self, file_):
        return self.split(file_)[2]

    def check_path(self, file_):

        path_ = self.path(file_)

        if not os.path.exists(path_):
            os.makedirs(path_)

    @staticmethod
    def sanitize_filename(filename):
        return filename.replace('/', '_')

    def no_ext(self, file_):
        return os.path.join(self.path(file_), self.name(file_))

    def change_ext(self, file_, new_ext):
        return f'{self.no_ext(file_)}.{new_ext}'
