

class PWException(Exception):
    def __init__(self, msg, code=0):
        self.msg = msg
        self.code = code

    def __str__(self):
        return self.msg

