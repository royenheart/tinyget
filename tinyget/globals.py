import os
from enum import Enum
from typing import Dict, List, Union
from tinyget.repos import BUILTIN_REPO
import platform

DEFAULT_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
DEFAULT_LIVE_OUTPUT = True

global_configs: Dict[str, Union[str, List[str], bool]] = {
    "repo_path": [BUILTIN_REPO],
    "LOCALE_DIR": DEFAULT_LOCALE_DIR,
    "live_output": DEFAULT_LIVE_OUTPUT,
}


class SupportArchs(Enum):
    x86_64 = "x86_64"
    mips = "mips"
    loongarch64 = "loongarch64"
    arm64 = "arm64"

    def __eq__(self, value: object) -> bool:
        return self.name == value

    def __str__(self) -> str:
        return self.name


ARCH = platform.machine()

# tinyget retcode
SUCCESS = 0
ERROR_HANDLED = 1
ERROR_UNKNOWN = 3
