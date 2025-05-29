

import logging
from logging.handlers import TimedRotatingFileHandler


def init_log_4_rotate(file_name, name=None):
    import logging
    from logging.handlers import TimedRotatingFileHandler

    log_fmt = '%(asctime)s - %(filename)s[%(lineno)d] - %(levelname)s: %(message)s'
    formatter = logging.Formatter(log_fmt)
    log_file_handler = TimedRotatingFileHandler(filename=file_name, when="D", interval=1, backupCount=10)
    log_file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(name)
    log.addHandler(log_file_handler)

    return log





