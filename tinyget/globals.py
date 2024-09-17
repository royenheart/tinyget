import os

DEFAULT_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
DEFAULT_LIVE_OUTPUT = True

global_configs = {"LOCALE_DIR": DEFAULT_LOCALE_DIR, "live_output": DEFAULT_LIVE_OUTPUT}

# tinyget retcode
SUCCESS = 0
ERROR_HANDLED = 1
ERROR_UNKNOWN = 3
