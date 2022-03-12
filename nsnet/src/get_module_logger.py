import sys
import logging
def get_module_logger(name=None):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)8s | %(message)s')
    
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter) 

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger