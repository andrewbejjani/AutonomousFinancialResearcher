import logging
import sys

def get_logger(module_name: str):
    """
    logging mechanism that outputs to both the console and a file.
    relied on https://docs.python.org/3/howto/logging.html# for documentation and examples
    """
    # we need a logger which is specific to the file which called it
    logger = logging.getLogger(module_name)
    
    # there are different logging levels (debug is a lower level which is
    # a bit spammy so we avoid polluting the logs by default, unless we want
    # to debug an issue then we set it to DEBUG)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # standardized log format
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # we create the console handler which will output the logs to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger