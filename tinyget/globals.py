import os

DEFAULT_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")

global_configs = {"LOCALE_DIR": DEFAULT_LOCALE_DIR}

# tinyget retcode
SUCCESS = 0
ERROR_HANDLED = 1
ERROR_UNKNOWN = 3
