from .process import execute_command as _execute_command, CommandExecutionError
from .ai_helper import (
    AIHelper,
    AIHelperHostError,
    AIHelperKeyError,
    try_to_get_ai_helper,
)
from typing import Union, List
from rich.panel import Panel
from rich.console import Console
import traceback
import click
import sys

ai_helper = try_to_get_ai_helper()

if ai_helper is None:
    execute_command = _execute_command
else:

    def execute_command(
        args: Union[List[str], str], envp: dict = {}, timeout: int = None
    ):
        try:
            result = _execute_command(args, envp, timeout)
        except CommandExecutionError as e:
            recommendation = ai_helper.fix_command(args, e.stdout, e.stderr)
            console = Console()
            console.print(
                Panel(
                    recommendation,
                    border_style="green",
                    title="来自AI助手的建议",
                )
            )
            console.print(
                Panel(traceback.format_exc(), border_style="red", title="原始错误")
            )
            sys.exit(0)
        except Exception:
            raise
        return result
