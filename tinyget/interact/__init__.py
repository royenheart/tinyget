from .process import execute_command as _execute_command
from .process import just_execute
from .ai_helper import (
    AIHelper,
    AIHelperHostError,
    AIHelperKeyError,
    try_to_get_ai_helper,
)
from typing import Optional, Union, List
from ..common_utils import logger
from tinyget.globals import global_configs


def execute_command(
    args: Union[List[str], str],
    envp: dict = {},
    timeout: Optional[float] = None,
    cwd: Optional[str] = None,
):
    logger.debug(f"Execute command: {args}. Env params: {envp}")
    live_output = global_configs["live_output"]
    result = _execute_command(
        args, envp, timeout, cwd, realtime_output=bool(live_output)
    )
    return result
